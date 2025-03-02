import logging
import pymrio
import pandas as pd

# -------------------------------------------------------------------------
# Configure logging to display DEBUG messages on the console
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_custom_gwp_csv(
    path_to_exiobase3,
    output_csv_name="exiobase_gwp_factors.csv"
):
    """
    1) Parse EXIOBASE 3 data at `path_to_exiobase3`.
    2) Compute the main IO system (including L).
    3) Sum specified GHG flows (CO2, CH4, N2O) from the S matrix
       into one 'Global Warming (GWP100)' row.
    4) Multiply by L to get supply-chain multipliers for each region×sector.
    5) Save the final multipliers to CSV.
    """
    
    logging.info("=== Starting create_custom_gwp_csv ===")
    logging.info(f"Will parse EXIOBASE 3 from: {path_to_exiobase3}")
    logging.info(f"Output CSV will be: {output_csv_name}")

    # 1. Parse EXIOBASE 3 from local folder or .zip
    logging.debug("Parsing EXIOBASE 3 data...")
    exio = pymrio.parse_exiobase3(path=path_to_exiobase3)
    logging.debug("Parsing complete.")

    # 2. Calculate all required system matrices (A, x, L, etc.)
    logging.debug("Running exio.calc_all() to compute the IO system and related matrices...")
    exio.calc_all()
    logging.debug("Calculation of the IO system is done.")

    # 3. Access the S matrix (which stores extension intensities)
    #    In some EXIOBASE versions, you might use exio.satellite["emissions"].S
    logging.debug("Looking for exio.satellite.S matrix...")
    if not hasattr(exio.satellite, "S") or exio.satellite.S is None:
        logging.error("No `S` matrix found under `exio.satellite.S`!")
        logging.error(f"Available satellite keys: {list(exio.satellite.keys())}")
        raise ValueError(
            "No `S` matrix found under `exio.satellite.S`!\n"
            f"Available satellite keys: {list(exio.satellite.keys())}"
        )
    S_df = exio.satellite.S
    logging.info(f"S matrix found with shape {S_df.shape}.")
    logging.info(f"First few rows of S_df index: {list(S_df.index[:5])}")
    logging.info(f"First few columns of S_df: {S_df.columns[:5]}")

    # 4. Define the GHG flows in your dataset
    ghg_flows = [
        "CO2 - combustion - air",
        "CH4 - combustion - air",
        "N2O - combustion - air",
    ]
    logging.info(f"GHG flow names we are summing: {ghg_flows}")

    # 5. Set GWP100 factors (AR5 100-year)
    cf_map = {
        "CO2 - combustion - air": 1.0,
        "CH4 - combustion - air": 28.0,
        "N2O - combustion - air": 265.0
    }
    logging.info(f"Using GWP100 factors: {cf_map}")

    # Verify which flows exist in the dataset
    ghg_flows_found = [flow for flow in ghg_flows if flow in S_df.index]
    logging.debug(f"GHG flows found in S_df: {ghg_flows_found}")
    if not ghg_flows_found:
        logging.error("None of the specified GHG flow names were found in S_df.index!")
        raise ValueError(
            "None of the specified GHG flow names were found in S_df.index!\n"
            f"  Specified: {ghg_flows}\n"
            f"  Actual index (sample): {list(S_df.index)[:50]}"
        )

    # 6. Create a combined row "Global Warming (GWP100)" by summing each flow * factor
    logging.debug("Creating aggregated GWP100 row from the flows found.")
    S_agg = pd.Series(0.0, index=S_df.columns, name="Global Warming (GWP100)")
    for flow in ghg_flows_found:
        factor = cf_map.get(flow, 0.0)
        logging.debug(f"Adding flow '{flow}' with factor {factor}.")
        S_agg += factor * S_df.loc[flow]
    logging.info(f"Finished summing GHG flows into a single row. S_agg shape: {S_agg.shape}")

    # 7. Multiply by the Leontief inverse (L) => supply-chain multipliers
    logging.debug("Retrieving the Leontief inverse (L) matrix.")
    L = exio.L
    logging.debug(f"L matrix shape: {L.shape}")
    logging.debug("Performing the matrix multiplication: S_agg @ L")
    M_agg = S_agg @ L  # yields (1×n) supply-chain multipliers
    logging.info("Supply-chain multipliers computed successfully.")

    # 8. Convert to DataFrame
    M_agg_df = M_agg.to_frame(name="GWP100 [kg CO2-eq/unit output]")
    # Rename index levels
    M_agg_df.index.set_names(["Region", "Sector"], inplace=True)

    # 9. Save to CSV
    logging.debug(f"Writing results to {output_csv_name}...")
    M_agg_df.to_csv(output_csv_name)
    logging.info(f"Saved GWP100 multipliers to '{output_csv_name}'.")
    logging.info(
        "Index = (Region, Sector), Column = 'GWP100 [kg CO2-eq/unit output]'."
    )
    logging.info("=== create_custom_gwp_csv completed successfully. ===")


if __name__ == "__main__":
    # Adjust path if needed
    path_to_exiobase3 = "./IOT_2022_pxp"
    create_custom_gwp_csv(path_to_exiobase3)
