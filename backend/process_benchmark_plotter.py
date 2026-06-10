"""
process_benchmark_plotter.py

A reusable benchmarking and reporting module for comparing the
environmental and operational performance of two industrial processes.

The module loads simulation outputs from an original process and an
optimized process, converts the daily time-series data into Pandas
DataFrames, computes KPIs and savings, and generates various plots
for energy consumption, water usage, emissions, products, byproducts,
correlations, and monthly trends.

Outputs
-------
- PNG graphs
- CSV summary tables

Typical usage
-------------
plotter = ProcessBenchmarkPlotter(
    "simulation_analytics_original.json",
    "simulation_analytics_optimized.json"
)

plotter.generate_all()
"""

import json
import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from scipy.stats import gaussian_kde
from scipy.stats import pearsonr


class ProcessBenchmarkPlotter:
    """
    Generates benchmark reports for comparing original and optimized
    industrial processes.

    The class converts simulation outputs into structured DataFrames,
    computes performance indicators, and creates graphical reports
    showing improvements in sustainability metrics.

    Parameters
    ----------
    original_json : str
        Path to the original process simulation JSON file.

    optimized_json : str
        Path to the optimized process simulation JSON file.

    output_dir : str, optional
        Directory where generated graphs and reports will be saved.
        Default is "benchmark_report".
    """

    def __init__(self, original_json, optimized_json, output_dir="benchmark_report"):
        """
        Initialize the benchmark plotter and load simulation data.

        Parameters
        ----------
        original_json : str
            Path to the original simulation output.

        optimized_json : str
            Path to the optimized simulation output.

        output_dir : str
            Destination directory for generated reports.
        """
        self.original_json = original_json
        self.optimized_json = optimized_json
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.load_data()

    def load_data(self):
        """
        Load both simulation files and convert their daily time series
        into Pandas DataFrames.

        Date columns are automatically converted into datetime objects
        to enable time-based analysis and resampling.
        """
        with open(self.original_json) as f:
            original = json.load(f)

        with open(self.optimized_json) as f:
            optimized = json.load(f)

        self.original_df = self.flatten_daily_series(original["daily_series"])

        self.optimized_df = self.flatten_daily_series(optimized["daily_series"])

        self.original_df["date"] = pd.to_datetime(self.original_df["date"])

        self.optimized_df["date"] = pd.to_datetime(self.optimized_df["date"])

    def flatten_daily_series(self, daily_series):
        """
        Convert nested daily simulation records into a flat DataFrame.

        Each metric category (energy, water, products, emissions, etc.)
        is expanded into separate columns using dot notation.

        Parameters
        ----------
        daily_series : list
            Daily records from the simulation JSON.

        Returns
        -------
        pandas.DataFrame
            Flattened tabular representation of the daily data.
        """
        rows = []

        for day in daily_series:

            row = {"date": day["date"]}

            for category in [
                "energy_consumption",
                "water_usage",
                "raw_materials",
                "products",
                "byproducts",
                "emissions",
            ]:

                if category in day:

                    for k, v in day[category].items():

                        row[f"{category}.{k}"] = v

            rows.append(row)

        return pd.DataFrame(rows)

    def aggregate_monthly(self):
        """
        Aggregate daily metrics into monthly totals.

        Returns
        -------
        tuple[pandas.DataFrame, pandas.DataFrame]
            Monthly aggregated data for the original and optimized processes.
        """
        original = self.original_df.set_index("date").resample("ME").sum()

        optimized = self.optimized_df.set_index("date").resample("ME").sum()

        return original, optimized

    def compute_kpis(self):
        """
        Calculate total values of all metrics over the simulation period.

        Returns
        -------
        pandas.DataFrame
            KPI table containing totals for both processes.
        """
        return pd.DataFrame(
            {
                "Original Total": self.original_df.drop(columns="date").sum(),
                "Optimized Total": self.optimized_df.drop(columns="date").sum(),
            }
        )

    def compute_savings(self):
        """
        Compute absolute and percentage improvements achieved by the
        optimized process.

        Returns
        -------
        pandas.DataFrame
            Table containing:

            - Absolute Saving
            - Percent Saving
        """
        cols = sorted(set(self.original_df.columns) | set(self.optimized_df.columns))

        cols.remove("date")

        original = self.original_df.reindex(columns=cols, fill_value=0).sum()
        optimized = self.optimized_df.reindex(columns=cols, fill_value=0).sum()

        savings = original - optimized

        percent = 100 * savings / original

        return pd.DataFrame({"Absolute Saving": savings, "Percent Saving": percent})

    # ---- plotting ----
    def plot_energy(self):
        """
        Generate a line plot showing daily energy consumption for both
        processes.

        Output
        ------
        energy.png
        """
        plt.figure(figsize=(12, 6))

        plt.plot(
            self.original_df["date"],
            self.original_df["energy_consumption.MWh"],
            label="Original",
        )

        plt.plot(
            self.optimized_df["date"],
            self.optimized_df["energy_consumption.MWh"],
            label="Optimized",
        )

        plt.ylabel("Energy (MWh)")
        plt.title(
            "Daily Energy Consumption\n"
            "Shows how much electricity each process uses every day "
            "(lower values mean lower operating cost and environmental impact)"
        )

        plt.grid()
        plt.legend()

        self.save_fig("energy")

    def plot_water(self):
        """
        Generate a daily water usage comparison chart.

        Output
        ------
        water.png
        """
        plt.figure(figsize=(12, 6))

        plt.plot(
            self.original_df["date"],
            self.original_df["water_usage.m3"],
            label="Original",
        )

        plt.plot(
            self.optimized_df["date"],
            self.optimized_df["water_usage.m3"],
            label="Optimized",
        )

        plt.ylabel("Water (m³)")
        plt.title(
            "Daily Water Usage\n"
            "Shows how much water is consumed each day "
            "(lower values indicate better water conservation)"
        )

        plt.legend()
        plt.grid()

        self.save_fig("water")

    def plot_emissions(self):
        """
        Generate a grouped bar chart comparing total emissions produced
        by each process.

        Output
        ------
        emissions.png
        """
        cols = sorted(
            set(c for c in self.original_df.columns if c.startswith("emissions."))
            | set(c for c in self.optimized_df.columns if c.startswith("emissions."))
        )

        original = self.original_df.reindex(columns=cols, fill_value=0).sum()
        optimized = self.optimized_df.reindex(columns=cols, fill_value=0).sum()

        x = np.arange(len(cols))
        width = 0.4

        plt.figure(figsize=(14, 7))

        plt.bar(x - width / 2, original, width, label="Original")

        plt.bar(x + width / 2, optimized, width, label="Optimized")

        plt.xticks(
            x, [clean_label(c.replace("emissions.", "")) for c in cols], rotation=45
        )

        plt.legend()
        plt.title(
            "Total Pollutants Released into the Environment\n"
            "Compares greenhouse gases and other emissions "
            "(smaller bars are better)"
        )

        self.save_fig("emissions")

    def plot_raw_materials(self):
        """
        Visualize the largest reductions in raw material consumption.

        Output
        ------
        raw_materials.png
        """
        cols = sorted(
            set(c for c in self.original_df.columns if c.startswith("raw_materials."))
            | set(
                c for c in self.optimized_df.columns if c.startswith("raw_materials.")
            )
        )

        original = self.original_df.reindex(columns=cols, fill_value=0).sum()

        optimized = self.optimized_df.reindex(columns=cols, fill_value=0).sum()

        savings = original - optimized

        savings.sort_values().tail(15).plot.barh(figsize=(10, 8))

        plt.title(
            "Reduction in Raw Material Consumption\n"
            "Shows which materials are saved by the optimized process "
            "(larger bars mean greater savings)"
        )

        self.save_fig("raw_materials")

    def plot_products(self):
        """
        Compare total product outputs produced by both processes.

        Output
        ------
        products.png
        """
        cols = sorted(
            set(c for c in self.original_df.columns if c.startswith("products."))
            | set(c for c in self.optimized_df.columns if c.startswith("products."))
        )

        original = self.original_df.reindex(columns=cols, fill_value=0).sum()

        optimized = self.optimized_df.reindex(columns=cols, fill_value=0).sum()

        df = pd.DataFrame(
            {
                "Original": original,
                "Optimized": optimized,
            }
        )

        # remove prefix for labels
        df.index = [clean_label(c.replace("products.", "")) for c in df.index]

        df.plot.bar(figsize=(14, 7))

        plt.xticks(rotation=90)
        plt.title(
            "Total Product Output\n"
            "Compares how much useful product each process produces "
            "(higher values indicate higher productivity)"
        )
        plt.ylabel("Total Production")

        self.save_fig("products")

    def plot_byproducts(self):
        """
        Visualize reductions in waste and byproducts achieved by the
        optimized process.

        Output
        ------
        byproducts.png
        """
        cols = sorted(
            set(c for c in self.original_df.columns if c.startswith("byproducts."))
            | set(c for c in self.optimized_df.columns if c.startswith("byproducts."))
        )

        original = self.original_df.reindex(columns=cols, fill_value=0).sum()

        optimized = self.optimized_df.reindex(columns=cols, fill_value=0).sum()

        diff = original - optimized

        diff.index = [clean_label(c.replace("byproducts.", "")) for c in diff.index]

        diff.sort_values().plot.barh(figsize=(10, 8))

        plt.title(
            "Waste and Byproduct Reduction\n"
            "Shows how much unwanted material is avoided "
            "(larger reductions are better)"
        )

        self.save_fig("byproducts")

    def plot_histograms(self):
        plt.figure(figsize=(10, 6))

        plt.hist(
            self.original_df["energy_consumption.MWh"],
            alpha=0.5,
            bins=30,
            label="Original",
        )

        plt.hist(
            self.optimized_df["energy_consumption.MWh"],
            alpha=0.5,
            bins=30,
            label="Optimized",
        )
        plt.title(
            "Distribution of Daily Energy Consumption\n"
            "Shows how frequently different energy usage levels occur"
        )

        plt.legend()

        self.save_fig("histograms")

    def plot_distributions(self):
        plt.figure(figsize=(10, 6))

        sns.kdeplot(self.original_df["energy_consumption.MWh"], label="Original")

        sns.kdeplot(self.optimized_df["energy_consumption.MWh"], label="Optimized")
        plt.title(
            "Typical Energy Usage Patterns\n"
            "Shows the probability of different daily energy levels"
        )

        plt.legend()

        self.save_fig("distribution")

    def plot_boxplots(self):
        plt.figure(figsize=(8, 6))

        plt.boxplot(
            [
                self.original_df["energy_consumption.MWh"],
                self.optimized_df["energy_consumption.MWh"],
            ]
        )
        plt.title(
            "Variation in Daily Energy Consumption\n"
            "Shows average usage and day-to-day fluctuations "
            "(smaller spread means more stable operation)"
        )

        plt.xticks([1, 2], ["Original", "Optimized"])

        self.save_fig("boxplot")

    def plot_cumulative_metrics(self):
        plt.figure(figsize=(12, 6))

        plt.plot(
            self.original_df["date"],
            self.original_df["energy_consumption.MWh"].cumsum(),
            label="Original",
        )

        plt.plot(
            self.optimized_df["date"],
            self.optimized_df["energy_consumption.MWh"].cumsum(),
            label="Optimized",
        )

        plt.title(
            "Total Energy Used Over Time\n"
            "Shows how energy costs accumulate throughout the year "
            "(lower curve indicates better efficiency)"
        )

        plt.legend()

        self.save_fig("cumulative_energy")

    def plot_heatmap(self):
        """
        Generate a correlation heatmap of all process variables.

        Output
        ------
        heatmap.png
        """
        corr = self.original_df.drop(columns="date").corr()

        plt.figure(figsize=(14, 12))

        sns.heatmap(corr, cmap="coolwarm")

        plt.title(
            "Relationship Between Process Variables\n"
            "Shows which factors tend to increase or decrease together"
        )

        self.save_fig("heatmap")

    def plot_correlation_matrix(self):
        cols = ["energy_consumption.MWh", "water_usage.m3"]

        sns.pairplot(self.original_df[cols])

        plt.savefig(os.path.join(self.output_dir, "correlation_matrix.png"))

        plt.close()

    def plot_monthly_dashboard(self):
        """
        Create a monthly energy consumption dashboard showing trends
        throughout the year.

        Output
        ------
        monthly_dashboard.png
        """
        original, optimized = self.aggregate_monthly()

        plt.figure(figsize=(14, 6))

        plt.plot(original.index, original["energy_consumption.MWh"], label="Original")

        plt.plot(
            optimized.index, optimized["energy_consumption.MWh"], label="Optimized"
        )

        plt.title(
            "Monthly Energy Consumption Trend\n"
            "Shows how energy demand changes throughout the year"
        )

        plt.legend()

        self.save_fig("monthly_dashboard")

    def create_summary_table(self):
        """
        Create and save a CSV file summarizing absolute and percentage
        savings achieved by the optimized process.

        Returns
        -------
        pandas.DataFrame
            Savings summary table.

        Output
        ------
        summary.csv
        """
        df = self.compute_savings()

        df.to_csv(os.path.join(self.output_dir, "summary.csv"))
        return df

    def generate_all(self):
        """
        Generate the complete benchmark report.

        This method executes all visualization functions and produces
        the summary CSV file.

        Generated Outputs
        -----------------
        - Energy comparison
        - Water comparison
        - Emissions comparison
        - Product comparison
        - Byproduct reduction
        - Distribution plots
        - Correlation plots
        - Heatmaps
        - Monthly dashboard
        - Summary CSV
        """
        self.plot_energy()
        self.plot_water()
        self.plot_emissions()
        self.plot_raw_materials()
        self.plot_products()
        self.plot_byproducts()
        self.plot_histograms()
        self.plot_distributions()
        self.plot_boxplots()
        self.plot_cumulative_metrics()
        self.plot_heatmap()
        self.plot_correlation_matrix()
        self.plot_monthly_dashboard()

        self.create_summary_table()

    def save_fig(self, name):
        """
        Save the current Matplotlib figure to disk and release memory.

        Parameters
        ----------
        name : str
            Output filename without extension.
        """
        plt.tight_layout()

        plt.savefig(os.path.join(self.output_dir, f"{name}.png"), dpi=300)

        plt.close()


def clean_label(label):
    """
    Replace Unicode subscripts and special symbols with ASCII
    equivalents to improve plot compatibility and font support.

    Parameters
    ----------
    label : str

    Returns
    -------
    str
        Sanitized label suitable for graph rendering.
    """
    return (
        label.replace("CO₂", "CO2")
        .replace("m³", "m3")
        .replace("₀", "0")
        .replace("₁", "1")
        .replace("₂", "2")
        .replace("₃", "3")
        .replace("₄", "4")
        .replace("₅", "5")
        .replace("₆", "6")
        .replace("₇", "7")
        .replace("₈", "8")
        .replace("₉", "9")
    )
