import deepxde as dde
from . import EquationBase, Constants
from ..parameter import EquationParameter

class MCEquationParameter(EquationParameter, Constants):
    """ default parameters for mass conservation
    """
    _EQUATION_TYPE = 'MC' 
    def __init__(self, param_dict={}):
        # load necessary constants
        Constants.__init__(self)
        super().__init__(param_dict)

    def set_default(self):
        self.input = ['x', 'y']
        self.output = ['u', 'v', 'a', 'H']
        self.output_lb = [self.variable_lb[k] for k in self.output]
        self.output_ub = [self.variable_ub[k] for k in self.output]
        self.data_weights = [1.0e-8*self.yts**2, 1.0e-8*self.yts**2, 1.0*self.yts**2, 1.0e-6]
        self.residuals = ["f"+self._EQUATION_TYPE]
        self.pde_weights = [1.0e8]

        # scalar variables: name:value
        self.scalar_variables = {
                'n': 3.0,               # exponent of Glen's flow law
                'B':1.26802073401e+08   # -8 degree C, cuffey
                }

class MC(EquationBase): #{{{
    """ MC on 2D problem with uniform B
    """
    _EQUATION_TYPE = 'MC' 
    def __init__(self, parameters=MCEquationParameter()):
        super().__init__(parameters)

    def pde(self, nn_input_var, nn_output_var):
        """ residual of MC 2D PDE

        Args:
            nn_input_var: global input to the nn
            nn_output_var: global output from the nn
        """
        # get the ids
        xid = self.local_input_var["x"]
        yid = self.local_input_var["y"]

        uid = self.local_output_var["u"]
        vid = self.local_output_var["v"]
        aid = self.local_output_var["a"]
        Hid = self.local_output_var["H"]

        # unpacking normalized output
        u, v, a, H = nn_output_var[:, uid:uid+1], nn_output_var[:, vid:vid+1], nn_output_var[:, aid:aid+1], nn_output_var[:, Hid:Hid+1]
    
        # spatial derivatives
        u_x = dde.grad.jacobian(nn_output_var, nn_input_var, i=uid, j=xid)
        H_x = dde.grad.jacobian(nn_output_var, nn_input_var, i=Hid, j=xid)
        v_y = dde.grad.jacobian(nn_output_var, nn_input_var, i=vid, j=yid)
        H_y = dde.grad.jacobian(nn_output_var, nn_input_var, i=Hid, j=yid)
    
        # residual
        f = H*u_x + H_x*u + H*v_y + H_y*v - a
    
        return [f] #}}}



