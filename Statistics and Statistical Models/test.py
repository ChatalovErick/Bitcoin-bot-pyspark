import numpy as np
from scipy.optimize import minimize
from scipy.special import gamma, gammaln, norm
import pandas as pd

# ------------------------------------------------------------- #
# normal distribution #
# ------------------------------------------------------------- #

class log_likelihood_normal():
    
    def __init__(self,data):
        self.data = data
        print(self.data)
        # Initial guess for mu and sigma   
        self.optimization()
    
    def log_likelihood_normal(params,data):
        mu, sigma = params
        n = len(data)
        log_likelihood_value = -0.5 * n * np.log(2 * np.pi * sigma ** 2) - (1 / (2 * sigma ** 2)) * np.sum((data - mu) ** 2)
        return -log_likelihood_value  # Negate for minimization

    def optimization(self):
        initial_guess = [np.mean(self.data), np.std(self.data)]
        result = minimize(log_likelihood_normal, initial_guess, args=(self.data), method='L-BFGS-B', bounds=[(None, None), (1e-5, None)])

        self.mu_est, self.sigma_est = result.x
        print(self.mu_est)
        print(self.sigma_est)
        """
        print(f'Estimated mu: {mu_est}')
        print(f'Estimated sigma: {sigma_est}')

        # Create a range of values for the x-axis
        x = np.linspace(min(data), max(data), 1000)

        # Calculate the Normal PDF with the estimated parameters
        y = norm.pdf(x, loc=mu_est, scale=sigma_est)

        # Plot the Normal PDF
        plt.plot(x, y, 'r-', lw=2, label=f'Normal Distribution\n(mu={mu_est:.2f}, sigma={sigma_est:.2f})')
        plt.show()
        """

match_trades = pd.read_pickle("data gathering and storage/Data transfer and local storage/dailydata/MatchTrades_data/MatchTrades 04-11-2024.pickle")
match_trades.set_index('trade_date', inplace=True)
data = list(((match_trades["22:22:14":"23:22:14"])["price"]).apply(float))

log_likelihood_normal(data)