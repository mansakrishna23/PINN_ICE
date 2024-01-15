import deepxde as dde
import numpy as np

from . import physics
from . import domain
from .parameters import Parameters
from .modeldata import Data
from .nn import NN


class PINN:
    """
    class of a PINN model
    """
    def __init__(self, params={}, training_data=Data()):
        # initialize data
        self.param = Parameters(params)

        # main components
        self.domain = domain.Domain(self.param.domain.shapefile)
        self.param.nn.set_parameters({"input_lb": self.domain.geometry.bbox[0,:], "input_ub": self.domain.geometry.bbox[1,:]})

        # training data
        self.training_data = [dde.icbc.PointSetBC(training_data.X[d], training_data.sol[d], component=i) 
                for i,d in enumerate(self.param.physics.variables) if d in training_data.sol]

        # check if training data exceed the scaling range, also wrap output_lb and output_ub with np.array
        for i,d in enumerate(self.param.physics.variables):
            if d in training_data.sol:
                if np.max(training_data.sol[d]) > self.param.nn.output_ub[i]:
                    self.param.nn.output_ub[i] = np.max(training_data.sol[d])
                if np.min(training_data.sol[d]) < self.param.nn.output_lb[i]:
                    self.param.nn.output_lb[i] = np.min(training_data.sol[d])
        self.param.nn.output_lb = np.array(self.param.nn.output_lb)
        self.param.nn.output_ub = np.array(self.param.nn.output_ub)

        # set physics
        self.physics = physics.SSA2DUniformMu(params["mu"])

        #  deepxde data object
        self.data = dde.data.PDE(
                self.domain.geometry,
                self.physics.pde,
                self.training_data,  # all the data loss will be evaluated
                num_domain=self.param.domain.num_collocation_points, # collocation points
                num_boundary=0,  # no need to set for data misfit, unless add calving front boundary, etc.
                num_test=None)

        # define the neural network in use
        self.nn = NN(self.param.nn)

        # setup the deepxde model
        self.model = dde.Model(self.data, self.nn.net)

    # TODO: add update data, update net, ...

    def compile(self, opt=None, loss=None, lr=None, loss_weights=None):
        """
        compile the model  
        """
        # load from param
        if opt is None:
            opt = self.param.training.optimizer

        if loss is None:
            loss = self.param.training.loss_function

        if lr is None:
            lr = self.param.training.learning_rate

        if loss_weights is None:
            loss_weights = self.param.training.loss_weights

        # compile the model
        self.model.compile(opt, loss=loss, lr=0.001, loss_weights=loss_weights)

    def train(self):
        self.loss_history, self.train_state = self.model.train(iterations=self.param.training.epochs, 
                display_every=10000, disregard_previous_best=True)

        #dde.saveplot(loss_history, train_state, issave=True, isplot=False, output_dir=modelFolder)

        #model.save(modelFolder+"pinn/model")

