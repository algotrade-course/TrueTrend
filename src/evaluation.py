import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import pandas as pd
import os

def maximumDrawdown(portfolio_series):
    if len(portfolio_series) == 0 or not np.all(np.isfinite(portfolio_series)):
        return (0, np.array([]))
    peak = np.maximum.accumulate(portfolio_series)
    drawdown = (portfolio_series - peak) / peak
    mdd = np.min(drawdown) if len(drawdown) > 0 else 0
    return (mdd, drawdown)

# def sharpRatio(portfolio_series, rf_rate=0.03, periods_per_year=252):
#     if len(portfolio_series) < 2 or not np.all(np.isfinite(portfolio_series)):
#         return 0

#     daily_returns = np.diff(portfolio_series) / portfolio_series[:-1]

#     excess_daily_returns = daily_returns - rf_rate / periods_per_year

#     mean_excess_return = np.mean(excess_daily_returns)
#     std_excess_return = np.std(excess_daily_returns)

#     if std_excess_return == 0:
#         return 0

#     sharpe_ratio = (mean_excess_return / std_excess_return) * np.sqrt(periods_per_year)
#     return sharpe_ratio

def sharpe_ratio(portfolio_series, rf_rate=0.03, periods_per_year=252):
    if len(portfolio_series) < 2 or not np.all(np.isfinite(portfolio_series)):
        return 0.0

    returns = np.diff(portfolio_series) / portfolio_series[:-1]

    rf_per_period = rf_rate / periods_per_year
    excess = returns - rf_per_period

    mean_excess = np.mean(excess)
    std_excess  = np.std(excess, ddof=1)
    if std_excess == 0:
        return 0.0

    return mean_excess / std_excess * np.sqrt(periods_per_year)

def plot_backtesting_results(input_csv, output_file="result/backtests.png", index=0):
    # Read the CSV
    df = pd.read_csv(input_csv)

    if "Date" not in df.columns or "Portfolio Value" not in df.columns:
        print(f"Error: {input_csv} is missing required columns 'Date' or 'Portfolio Value'.")
        return

    # Extract data
    
    portfolio_series = df["Portfolio Value"]

    # Calculate metrics
    mdd, drawdown = maximumDrawdown(portfolio_series)
    sharpe = sharpe_ratio(portfolio_series, rf_rate=0.03, periods_per_year=len(portfolio_series))


    dates = pd.to_datetime(df["Date"])
    # Plotting
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(dates, portfolio_series, label="Portfolio Value", color="blue", linewidth=2)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Portfolio Value", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    ax2 = ax1.twinx()
    ax2.fill_between(dates, drawdown, 0, color="darkred", alpha=0.3, label="Drawdown")
    ax2.set_ylabel("Drawdown", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title(f"Backtesting Results\nMax Drawdown: {mdd:.2%} | Sharpe Ratio: {sharpe:.4f}")
    ax1.legend(loc="upper left")
    ax2.legend(loc="lower left")

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    base_name = os.path.splitext(output_file)[0]  # removes the .csv extension
    output = f"{base_name}.png"

    # Add suffix "_mdd_sharpe" before saving
    plt.savefig(output, dpi=300)
    print(f"Saved plot to {output_file}")
    plt.show()


def plot_all_portfolio_results(result_dir="result", output_file="result/all_backtests.png"):
    files = [f for f in os.listdir(result_dir) if f.startswith("portfolio_values_") and f.endswith(".csv")]
    if not files:
        print("No portfolio result files found.")
        return

    plt.figure(figsize=(14, 7))

    for file in files:
        path = os.path.join(result_dir, file)
        try:
            df = pd.read_csv(path)
            if "Date" not in df.columns or "Portfolio Value" not in df.columns:
                print(f"Skipping {file}: missing required columns.")
                continue

            portfolio_series = df["Portfolio Value"]
            df["Date"] = pd.to_datetime(df["Date"])
            
            mdd, drawdown = maximumDrawdown(portfolio_series)
            sharpe = sharpe_ratio(portfolio_series, rf_rate=0.03, periods_per_year=len(portfolio_series))

            label = f'Model: {file.replace("portfolio_values_", "").replace(".csv", "")}, SHARPE: {sharpe:.4f}, MDD: {mdd:.2%}'
            plt.plot(df["Date"], df["Portfolio Value"], label=label)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

    plt.title("Backtesting Result")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Save the plot
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300)
    print(f"Saved plot to {output_file}")

    plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot backtesting results from a CSV file.")
    parser.add_argument("--input_csv", required=True, help="Path to CSV file containing portfolio values")
    parser.add_argument("--output_file", required=True, help="Path to save the output plot")

    args = parser.parse_args()

    try:
        df = pd.read_csv(args.input_csv)
        if "Date" not in df.columns or "Portfolio Value" not in df.columns:
            raise ValueError("CSV must contain 'Date' and 'Portfolio Value' columns.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        exit(1)

    plot_backtesting_results(args.input_csv, args.output_file)
    print("Plotting complete.")