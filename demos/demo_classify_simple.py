#! /usr/bin/env python3
""" A La Carte GP Classification example on a simple square wave. """

import logging
import numpy as np
import matplotlib.pyplot as pl
from pyalacarte import classification, bases
# from pyalacarte.validation import logloss, errrate


#
# Settings
#

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# A la Carte classifier setting
nbases = 500
lenscale = 0.2
reg = 1000
method = 'SGD'
# method = 'SVI'
# method = 'MAP'
batchsize = 100
rate = 0.9
eta = 1e-6
passes = 1000

# Dataset Settings
Ntrain = 200
Npred = 3000


# Gen Data
X = np.linspace(-2 * np.pi, 2 * np.pi, Ntrain)[:, np.newaxis]
f = np.sin(X).flatten()
Y = np.round((f + 1) / 2)
Xs = np.linspace(-2.5 * np.pi, 2.5 * np.pi, Npred)[:, np.newaxis]


# Train
Phi = bases.RandomRBF(nbases, X.shape[1])
if method == 'SGD':
    weights, l = classification.logistic_sgd(X, Y, Phi, (lenscale,),
                                             regulariser=reg, eta=eta,
                                             batchsize=batchsize, rate=rate,
                                             passes=passes)
elif method == 'MAP':
    weights, l = classification.logistic_map(X, Y, Phi, (lenscale,),
                                             regulariser=reg)
elif method == 'SVI':
    params = classification.logistic_svi(X, Y, Phi, (lenscale,), passes=passes,
                                         regulariser=reg)
    weights, C, bparams, l = params
else:
    raise ValueError("Invalid method chosen!")


# Predict
if method != 'SVI':
    Ey = classification.logistic_predict(Xs, weights, Phi, (lenscale,))
else:
    # Ey = classification.logistic_predict(Xs, weights, Phi, bparams)
    Ey = classification.logistic_mpredict(Xs, weights, C, Phi, bparams)


# Plot
pl.figure()
ax = pl.subplot(111)
pl.plot(X, Y, 'k--', linewidth=2, label='Training data')
pl.plot(Xs, Ey, label='Prediction')
pl.grid(True)
pl.title('Classification Test')
pl.xlabel('X')
pl.ylabel('p(y* = 1)')
ax.set_ylim(-0.05, 1.05)
pl.legend()
pl.show()
