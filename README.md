# Algorithm Trading Project

This repository contains a collection of research notebooks and utility scripts for experimenting with quantitative trading strategies.

## Project Focus
- **Web crawling** data from Naver Finance and other public sources.
- **Collecting historical price data** for Korean equities (e.g., KOSPI200 constituents).
- **Constructing factor and signal matrices** to feed trading models.
- **Building, backtesting, and comparing** multiple algorithmic trading logics.
- **Rebalancing portfolios** based on logic performance, weights, and risk controls.
- **Generating trading decisions** (buy, sell, rebalance) using the tested strategies.

## Environment
- Trading is executed through **KOAStudioSA.exe (Kiwoom)**, which requires a 32-bit Windows environment.
- Python notebooks (`*.ipynb`) are used for prototyping logic, running simulations, and visualizing results.

## Repository Structure
- `*.ipynb` notebooks contain exploratory analysis, backtests, and data collection workflows.
- Python scripts such as `instant_trade&check_account.py` automate trading tasks and account checks.

## Data Sources
- Primary data is collected from **Naver Finance** web pages.

## Getting Started
1. Open the relevant notebook in Jupyter Lab or Jupyter Notebook.
2. Configure API keys or authentication for Kiwoom before running trading scripts.
3. Follow the workflow described in each notebook to replicate results or adapt them for new experiments.

## Contributing
Feel free to extend the notebooks or add new strategies. When updating the repository:
- Keep notebooks organized with clear markdown explanations.
- Document any new data sources or dependencies.
