from dataclasses import dataclass
import io
import seapipy.surface_evolver as surface_evolver

@dataclass
class SurfaceEvolverVM(surface_evolver.SurfaceEvolver):
    
    def generate_fe_file(self) -> io.StringIO:
        """
        Generate the initial Surface Evolver slate to write into

        :return: Initialized Surface Evolver slate
        :rtype: io.StringIO()
        """

        if not self.polygonal:
            self.add_refining_triangulation(3)
        return self.fe_file
    