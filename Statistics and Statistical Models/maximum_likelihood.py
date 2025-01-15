import numpy as np
from scipy.optimize import minimize
from scipy.special import gamma, gammaln, norm
import pandas as pd
import matplotlib.pyplot as plt

match_trades = pd.read_pickle("data gathering and storage/Data transfer and local storage/dailydata/MatchTrades_data/MatchTrades 04-11-2024.pickle")
match_trades.set_index('trade_date', inplace=True)
data = list(((match_trades["22:22:14":"23:22:14"])["price"]).apply(float))

# ------------------------------------------------------------- #
# gamma distribution #
# ------------------------------------------------------------- #

# Define the log-likelihood function for the Gamma distribution
def log_likelihood_gamma(params, data):
    alpha, beta = params
    n = len(data)
    log_likelihood_value = n * alpha * np.log(beta) - n * gammaln(alpha) + (alpha - 1) * np.sum(np.log(data)) - beta * np.sum(data)
    return -log_likelihood_value  # Negate for minimization

# Initial guess for alpha and beta
initial_guess = [1.0, 1.0]

# Perform the optimization to find alpha and beta that maximize the log-likelihood
result = minimize(log_likelihood_gamma, initial_guess, args=(data), method='L-BFGS-B', bounds=[(1e-5, None), (1e-5, None)])

alpha_est, beta_est = result.x
print(f'Estimated alpha: {alpha_est}')
print(f'Estimated beta: {beta_est}')

# Sample data: replace with your actual data
data = np.random.gamma(shape=alpha_est, scale=1/beta_est, size=1000)

# Estimated parameters
alpha_est = alpha_est
beta_est =  beta_est
# Create a range of values for the x-axis
x = np.linspace(0, np.max(data), 1000)

# Calculate the Gamma PDF with the estimated parameters
y = gamma.pdf(x, a=alpha_est, scale=1/beta_est)

# Plot the Gamma PDF
plt.plot(x, y, 'r-', lw=2, label=f'Gamma Distribution\n(alpha={alpha_est}, beta={beta_est})')
plt.show()

# ------------------------------------------------------------- #
# normal distribution #
# ------------------------------------------------------------- #

# Define the log-likelihood function for the normal distribution
def log_likelihood_normal(params, data):
    mu, sigma = params
    n = len(data)
    log_likelihood_value = -0.5 * n * np.log(2 * np.pi * sigma ** 2) - (1 / (2 * sigma ** 2)) * np.sum((data - mu) ** 2)
    return -log_likelihood_value  # Negate for minimization

# Initial guess for mu and sigma
initial_guess = [np.mean(data), np.std(data)]

# Perform the optimization to find mu and sigma that maximize the log-likelihood
result = minimize(log_likelihood_normal, initial_guess, args=(data), method='L-BFGS-B', bounds=[(None, None), (1e-5, None)])

mu_est, sigma_est = result.x
print(f'Estimated mu: {mu_est}')
print(f'Estimated sigma: {sigma_est}')

# Create a range of values for the x-axis
x = np.linspace(min(data), max(data), 1000)

# Calculate the Normal PDF with the estimated parameters
y = norm.pdf(x, loc=mu_est, scale=sigma_est)

# Plot the Normal PDF
plt.plot(x, y, 'r-', lw=2, label=f'Normal Distribution\n(mu={mu_est:.2f}, sigma={sigma_est:.2f})')
plt.show()


