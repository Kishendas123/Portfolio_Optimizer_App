import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_stock_data(tickers, start_date, end_date):
    """
    Retrieve Adjusted close prices input tickers and date range.
    """
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Adj Close']

def calculate_portfolio_performance(weights, mean_returns, cov_matrix):
    """
    Calculate Expected return and risk (standard deviation) of portfolio.
    """
    portfolio_return = np.sum(mean_returns * weights)
    portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_risk

def generate_random_weights(num_stocks):
    """
    Generating random weights and normalize them so that they sum up to 1.
    """
    weights = np.random.random(num_stocks)
    return weights / np.sum(weights)

def validate_ticker(ticker):
    """
    Validate ticker by attempting to download data
    Return True if valid, otherwise False
    """
    try:
        data = yf.download(ticker, period="1d")
        if data.empty:
            return False
        return True
    except Exception as e:
        return False

def validate_date(date_str):
    """
    Validate date format (YYYY-MM-DD)
    Return True if valid, otherwise False
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def optimize_portfolio(tickers, start_date, end_date, canvas_frame):
    """
    Optimize Portfolio by generating random portfolios and selecting the one with the lowest risk.
    Display the optimized potfolio's weights and plot the Efficient Frontier Curve.
    """
		#Step 1: Retrieve Stock data
    stock_data = get_stock_data(tickers, start_date, end_date)

		#Step 2: Check if the data is available.
    if stock_data.empty:
        messagebox.showerror("Error", "No data found for the given tickers and date range.")
        return

		#Step 3: Calculate returns, mean returns and covariance matrix
    returns = stock_data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

		#Step 4: Initialize variables to track best portfolio
    best_weights = None
    best_return = 0
    best_risk = float('inf')

		#Step 5: Generate random portfolios, Retrieve Portfolio Performance of all  portfolios
    num_portfolios = 10000
    all_returns = []
    all_risks = []
    all_weights = []

    for i in range(num_portfolios):
        weights = generate_random_weights(len(tickers))
        portfolio_return, portfolio_risk = calculate_portfolio_performance(weights, mean_returns, cov_matrix)
        all_returns.append(portfolio_return)
        all_risks.append(portfolio_risk)
        all_weights.append(weights)
        # Step 6: Update best portfolio if current portfolio has lower risk
        if portfolio_risk < best_risk:
            best_risk = portfolio_risk
            best_return = portfolio_return
            best_weights = weights
		# Step 7: Display the Optimized portfolio and plot the Efficient Frontier Curve.
    if best_weights is not None:
        result = "Optimized Portfolio Weights:\n"
        for ticker, weight in zip(tickers, best_weights):
            result += f"{ticker}: {weight:.2%}\n"

        result += f"\nOptimized Portfolio Return: {best_return:.2%}\n"
        result += f"Optimized Portfolio Risk (Standard Deviation): {best_risk:.2%}\n"

        # Display the result in the result_frame
        result_label.config(text=result)

        # Plotting the Efficient Frontier Curve on the Tkinter Canvas:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(all_risks, all_returns, c='blue', marker='o', s=10)
        ax.scatter([best_risk], [best_return], c='red', marker='x', s=100)
        ax.set_xlabel('Portfolio Risk (Standard Deviation)')
        ax.set_ylabel('Portfolio Return')
        ax.set_title('Efficient Frontier')

        # Clear the previous plot if any
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        # Embed the plot in Tkinter Canvas
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    else:
        messagebox.showerror("Error", "No valid weight combination found.")

def main():
    """
    Set up Tkinter GUI and handle user input for portfolio optmization.
    """
    def on_submit():
        """
        Handle the submit action, validate input and trigger portfolio optimization.
        """
        try:
            num_tickers = int(num_tickers_entry.get())
            if not (2 <= num_tickers <= 10):
                messagebox.showerror("Error", "Please enter a number between 2 and 10 for the number of tickers.")
                return

            tickers = []
            for i in range(num_tickers):
                ticker = ticker_entries[i].get().upper()
                if validate_ticker(ticker):
                    tickers.append(ticker)
                else:
                    messagebox.showerror("Error", f"Ticker '{ticker}' is invalid.")
                    return

            start_date = entry_start_date.get()
            end_date = entry_end_date.get()

            if not validate_date(start_date):
                messagebox.showerror("Error", "Invalid start date format. Please enter the date in YYYY-MM-DD format.")
                return

            if not validate_date(end_date):
                messagebox.showerror("Error", "Invalid end date format. Please enter the date in YYYY-MM-DD format.")
                return
						#Initialize Portfolio Optimization:
            optimize_portfolio(tickers, start_date, end_date, plot_frame)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid inputs.")

    def create_ticker_entries():
        """
        Create Dynamic Entry Fields for the number of tickers specified by the user.
        """
        #Clear any previous widget in the ticker_frame
        for widget in ticker_frame.winfo_children():
            widget.destroy()

        try:
            num_tickers = int(num_tickers_entry.get())
            if not (2 <= num_tickers <= 10):
                messagebox.showerror("Error", "Please enter a number between 2 and 10 for the Number of Tickers.")
                return

            global ticker_entries
            ticker_entries = []

            for i in range(num_tickers):
                ttk.Label(ticker_frame, text=f"Ticker {i + 1}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
                entry = ttk.Entry(ticker_frame)
                entry.grid(row=i, column=1, padx=5, pady=5)
                ticker_entries.append(entry)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for the number of tickers.")

    def on_closing():
        """
        Handle closing of Tkinter Application
        """
        # Properly close the Tkinter application and exit the program
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            root.quit()

    # Tkinter main container
    root = tk.Tk()
    root.title("Portfolio Optimization")
    root.configure(bg='#f0f0f0') # Light grey background

    style = ttk.Style()
    style.theme_use('xpnative')
    style.configure('TFrame', background='#f0f0f0') # Light grey background
    style.configure('TLabel', background='#f0f0f0', foreground='#333333') # Light grey background and dark grey letters
    style.configure('TButton', background='#ffffff', foreground='#333333', padding=6) # Light grey background and dark grey letters

    # Label and Entry widget for number of Tickers
    ttk.Label(root, text="Number of Tickers (2-10):").grid(row=0, column=0, padx=10, pady=10)
    num_tickers_entry = ttk.Entry(root)
    num_tickers_entry.grid(row=0, column=1, padx=10, pady=10)

    # Dynamically create entry fields with Label for the number of tickers to be entered using the function create_ticker_entries
    num_tickers_button = ttk.Button(root, text="Set Tickers", command=create_ticker_entries)
    num_tickers_button.grid(row=0, column=2, padx=10, pady=10)

    ticker_frame = ttk.Frame(root)
    ticker_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Label and Entry widget for Start Date and End Date
    ttk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10)
    entry_start_date = ttk.Entry(root)
    entry_start_date.grid(row=2, column=1, padx=10, pady=10)

    ttk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10)
    entry_end_date = ttk.Entry(root)
    entry_end_date.grid(row=3, column=1, padx=10, pady=10)

    # Call the function on_submit
    submit_button = ttk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    # Create a separate frame for the plot
    plot_frame = ttk.Frame(root)
    plot_frame.grid(row=0, column=3, rowspan=6, padx=10, pady=10, sticky="nsew")

    # Create a frame to display the optimization result
    result_frame = ttk.Frame(root)
    result_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Add a label to display the result
    global result_label
    result_label = ttk.Label(result_frame, text="", justify="left", anchor="nw")
    result_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Configure the grid to allow the plot frame to expand
    root.grid_columnconfigure(3, weight=1)
    root.grid_rowconfigure(5, weight=1)

    # Call the function on_closing to properly close the Tkinter application and exit the program
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()
