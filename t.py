import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import sys
import random
import math

class PerlinNoise(object):
    def __init__(self):
        self.grads = [151,160,137,91,90,15,
                    131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
                    190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
                    88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
                    77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
                    102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
                    135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
                    5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
                    223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
                    129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
                    251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
                    49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
                    138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]
        self.grid = 512*[None]
        self.cosine = False
        self.octaves = False

        for i in range(0, 256):
            self.grid[256+i] = self.grid[i] = self.grads[i]

    def randomize_grad(self):
        for i in range(0, 256):
            self.grads[i] = random.randint(1, 255)
        for i in range(0, 256):
            self.grid[256+i] = self.grid[i] = self.grads[i]

    def interpolate(self, x, x0, x1):
        return ((1 - x) * x0 + x * x1)

    def interpolate2(self, mu, y1, y2):
        mu2 = (1-math.cos(mu*math.pi))/2
        return(y1*(1-mu2)+y2*mu2)


    def fade(self, x):
        return 6*(x**5) - 15*(x**4) + 10*(x**3)

    def g(self, grad, x, y):
        s = grad & 3
        if s == 0:
            return x + y
        if s == 1:
            return -x + y
        if s == 2:
            return x - y
        if s == 3:
            return -x - y
        return 0

    def use_cosinterpol(self):
        if self.cosine == True : self.cosine = False
        else: self.cosine = True

    def use_octaves(self):
        if self.octaves == True : self.octaves = False
        else: self.octaves = True

    def noise(self, x, y):
        xi = math.floor(x) & 255
        yi = math.floor(y) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        
        g1 = self.grid[self.grid[xi]+yi]
        g2 = self.grid[self.grid[xi+1]+yi]
        g3 = self.grid[self.grid[xi]+yi+1]
        g4 = self.grid[self.grid[xi+1]+yi+1]
        
    
        d1 = self.g(g1, xf, yf)
        d2 = self.g(g2, xf - 1, yf)
        d3 = self.g(g3, xf, yf - 1)
        d4 = self.g(g4, xf - 1, yf - 1)
        
        u = self.fade(xf)
        v = self.fade(yf)
        
        if self.cosine:
            f = self.interpolate2
        else: f = self.interpolate
        x1 = f(u, d1, d2)
        x2 = f(u, d3, d4)
        noise = f(v, x1, x2)
        #return noise
        return (noise + 1) / 2

    def apply_octave(self, x, y, noctaves, persistence, lacunarity):
        noise_sum, sum_amp = 0, 0
        frequency, amplitude = 1, 1
        for i in range(0, noctaves):
            noise_sum += self.noise(x * frequency, y * frequency) * amplitude
            sum_amp += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return noise_sum/sum_amp


class Terrain(object):
    def set_fly(self, x):
        self.flying_const = x
        self.label_flying.setText('Flying(F): ' + str(self.flying_const))
    def set_amplitude(self, x):
        self.amplitude = x
        self.label_amplitude.setText('Amplitude(A): ' + str(self.amplitude))
    def set_wlength(self, x):
        self.wlength = x
        self.label_length.setText('Length(λ): ' + str(self.wlength))
    def set_flying(self):
        if self.flying == True : self.flying = False
        else: self.flying = True
    def set_octave(self, x):
        self.noctaves = x
        self.label_octaves.setText('Octaves: ' + str(self.noctaves))
    def set_persistence(self, x):
        self.persistence = x
        self.label_persistence.setText('Persistence: ' + str(self.persistence))
    def set_lacunarity(self, x):
        self.lacunarity = x
        self.label_lacunarity.setText('Lacunarity: ' + str(self.lacunarity))
    def set_scale(self, x):
        self.scale = x
        self.label_scale.setText('Scale: ' + str(self.scale))

    def __init__(self):
        self.pnoise = PerlinNoise()

        self.flying_const = 0.03
        self.amplitude = 50.0
        self.wlength = 0.1
        self.flying = False

        self.noctaves = 5
        self.persistence = 0.4
        self.lacunarity = 3.6
        self.scale = 40
        

        self.app = QtGui.QApplication(sys.argv)
    
        self.w = QtWidgets.QWidget()
        self.w.resize(800, 600)
        self.w.setWindowTitle('Perlin Noise')

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 6, 0)

        self.gbox_layout = QtWidgets.QFormLayout()
        self.gbox_layout.setContentsMargins(0, 10, 0, 0)

        self.options = QtWidgets.QGroupBox()
        self.options.setFixedWidth(250)
        self.options.setTitle('Cool things')
        self.options.setStyleSheet("""QGroupBox::title {
                                    subcontrol-origin: margin;
                                    top: 10px;
                                    left: 7px;
                                    padding: 0px 0px 0px 0px;
                                    }""")
        self.options.setLayout(self.gbox_layout)
        
        self.label_length = QtWidgets.QLabel()
        self.label_length.setText('Length(λ):')

        self.slider_length = QtWidgets.QSlider()
        self.slider_length.setRange(1, 100)
        self.slider_length.setOrientation(1)
        self.slider_length.valueChanged.connect(lambda x : self.set_wlength(x/100))
        self.slider_length.setValue(self.wlength*100)


        self.label_amplitude = QtWidgets.QLabel()
        self.label_amplitude.setText('Amplitude(A):')

        self.slider_ampl = QtWidgets.QSlider()
        self.slider_ampl.setRange(0, 100)
        self.slider_ampl.setOrientation(1)
        self.slider_ampl.valueChanged.connect(lambda x : self.set_amplitude(x/10))
        self.slider_ampl.setValue(self.amplitude)


        self.label_flying = QtWidgets.QLabel()
        self.label_flying.setText('Flying Const(F):')
        self.slider_fly = QtWidgets.QSlider()
        self.slider_fly.setRange(0, 100)
        self.slider_fly.setOrientation(1)
        self.slider_fly.valueChanged.connect(lambda x : self.set_fly(x/100))
        self.slider_fly.setValue(self.flying_const*100)

        self.cb_flying = QtWidgets.QCheckBox()
        self.cb_flying.setText('Fly Over')
        self.cb_flying.clicked.connect(self.set_flying)

        self.button_grad = QtWidgets.QPushButton()
        self.button_grad.setText('Randomize Gradient Vectors')
        self.button_grad.clicked.connect(self.pnoise.randomize_grad)

        self.cb_cosint = QtWidgets.QCheckBox()
        self.cb_cosint.setText('Cosine Interpolation')
        self.cb_cosint.clicked.connect(self.pnoise.use_cosinterpol)

        self.cb_octaves = QtWidgets.QCheckBox()
        self.cb_octaves.setText('Use Octaves')
        self.cb_octaves.clicked.connect(self.pnoise.use_octaves)

        self.label_octaves = QtWidgets.QLabel()
        self.label_octaves.setText('Octaves:')

        self.slider_oct = QtWidgets.QSlider()
        self.slider_oct.setRange(0, 10)
        self.slider_oct.setOrientation(1)
        self.slider_oct.valueChanged.connect(lambda x : self.set_octave(x))
        self.slider_oct.setValue(self.noctaves)

        self.label_persistence = QtWidgets.QLabel()
        self.label_persistence.setText('Persistence:')

        self.slider_per = QtWidgets.QSlider()
        self.slider_per.setRange(0, 10)
        self.slider_per.setOrientation(1)
        self.slider_per.valueChanged.connect(lambda x : self.set_persistence(x/10))
        self.slider_per.setValue(self.persistence*10)

        self.label_lacunarity = QtWidgets.QLabel()
        self.label_lacunarity.setText('Lacunarity:')

        self.slider_lac = QtWidgets.QSlider()
        self.slider_lac.setRange(0, 1000)
        self.slider_lac.setOrientation(1)
        self.slider_lac.valueChanged.connect(lambda x : self.set_lacunarity(x/10))
        self.slider_lac.setValue(self.lacunarity*10)

        self.label_scale = QtWidgets.QLabel()
        self.label_scale.setText('Scale:')

        self.slider_sca = QtWidgets.QSlider()
        self.slider_sca.setRange(0, 50)
        self.slider_sca.setOrientation(1)
        self.slider_sca.valueChanged.connect(lambda x : self.set_scale(x))
        self.slider_sca.setValue(self.scale)

        self.glw = gl.GLViewWidget()
        self.glw.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.glw.setCameraPosition(distance=100, elevation=25, azimuth = 45)

        self.n = 1
        self.x = range(0, 70, self.n)
        self.y = range(0, 70, self.n)
        self.p_faces = len(self.y)
        self.fly_inc = 0

        v = np.array([[0,0,0]])
        f = np.array([[0,0,0]])
        self.mesh = gl.GLMeshItem(vertexes=v, faces=f,
            smooth=False, drawEdges=True, drawFaces=False,
        )
        
        self.mesh.setGLOptions('additive')
        self.glw.addItem(self.mesh)

        self.layout.addWidget(self.glw)
        self.layout.addWidget(self.options)
        self.gbox_layout.addWidget(self.label_length)
        self.gbox_layout.addWidget(self.slider_length)
        self.gbox_layout.addWidget(self.label_amplitude)
        self.gbox_layout.addWidget(self.slider_ampl)
        self.gbox_layout.addWidget(self.label_flying)
        self.gbox_layout.addWidget(self.slider_fly)
        self.gbox_layout.addWidget(self.cb_flying)
        self.gbox_layout.addWidget(self.button_grad)
        self.gbox_layout.addWidget(self.cb_octaves)
        self.gbox_layout.addWidget(self.cb_cosint)
        self.gbox_layout.addWidget(self.label_octaves)
        self.gbox_layout.addWidget(self.slider_oct)
        self.gbox_layout.addWidget(self.label_persistence)
        self.gbox_layout.addWidget(self.slider_per)
        self.gbox_layout.addWidget(self.label_lacunarity)
        self.gbox_layout.addWidget(self.slider_lac)
        self.gbox_layout.addWidget(self.label_scale)
        self.gbox_layout.addWidget(self.slider_sca)

        self.w.setLayout(self.layout)
        self.w.show()

    def update(self):
        v = []
        for x in self.x:
            for y in self.y:
                if self.pnoise.octaves:
                    z = self.pnoise.apply_octave(x/len(self.x) + self.fly_inc, y/len(self.x) + self.fly_inc, self.noctaves, self.persistence, self.lacunarity)
                    v.append([x, y, self.scale*z])
                else:
                    z = self.amplitude * self.pnoise.noise((1/self.wlength)*(x/len(self.x)) + self.fly_inc, 
                                                            (1/self.wlength)*(y/len(self.x)) + self.fly_inc)
                    v.append([x, y, z])

        f = []
        for i in range(self.p_faces - 1):
            fixed_y = i * self.p_faces
            for j in range(self.p_faces - 1):
                f.append([j + fixed_y, fixed_y + j + self.p_faces, fixed_y + j + self.p_faces + 1])
                f.append([j + fixed_y, fixed_y + j + 1, fixed_y + j + self.p_faces + 1])

        f = np.array(f)
        self.mesh.setMeshData(vertexes=np.array(v), faces=f)
        
        if self.flying: self.fly_inc -= self.flying_const
        else: self.fly_inc = 0

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def initterrain(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(50)
        self.start()
        self.update()


if __name__ == '__main__':
    terrain = Terrain()
    terrain.initterrain()
