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
        
        # Top section
        self.fe_file.write("SPACE_DIMENSION 2 \n")
        self.fe_file.write("SCALE 0.005 FIXED\n")
        self.fe_file.write("STRING \n")
        
        # Global parameters
        self.fe_file.write("\n")
        self.fe_file.write(f"PARAMETER area_elasticity = {round(1.0, 3)}\n")
        self.fe_file.write(f"PARAMETER perimeter_contractility = {round(0.04, 3)}\n")
        
        # Cell parameters and energy functions
        self.fe_file.write("\n")
        for k, v in self.cells.items():
            i = abs(k)
            self.fe_file.write(f"METHOD_INSTANCE area_{i} METHOD edge_area\n")
            self.fe_file.write(f"METHOD_INSTANCE perimeter_{i} METHOD edge_length\n")
            self.fe_file.write(f"PARAMETER target_area_{i} = {round(self.volume_values[k], 3)}\n")
            self.fe_file.write(f"PARAMETER target_perimeter_{i} = {round(0, 3)}\n")
            self.fe_file.write(f"QUANTITY a_sq_{i} ENERGY FUNCTION 0.5 * area_elasticity * area_{i}.value^2\n")
            self.fe_file.write(f"QUANTITY a_lin_{i} ENERGY FUNCTION -area_elasticity * target_area_{i} * abs(area_{i}.value)\n")
            self.fe_file.write(f"QUANTITY p_sq_{i} ENERGY FUNCTION 0.5 * perimeter_contractility * perimeter_{i}.value^2\n")
            self.fe_file.write(f"QUANTITY p_lin_{i} ENERGY FUNCTION -perimeter_contractility * target_perimeter_{i} * perimeter_{i}.value\n")
            self.fe_file.write("\n")
        
        # Vertices
        self.fe_file.write("VERTICES \n")
        for k, v in self.vertices.items():
            self.fe_file.write(f"{k}   {round(v[0], 3)} {round(v[1], 3)}\n")
        
        # Build edge to cells mapping
        edge_to_cells = {}
        for cell_id, edge_list in self.cells.items():
            for edge_id in edge_list:
                absolute_edge_id = abs(edge_id)
                if absolute_edge_id not in edge_to_cells:
                    edge_to_cells[absolute_edge_id] = []
                edge_to_cells[absolute_edge_id].append(abs(cell_id))
        
        # Edges (with initial line tensions and references to adjacent cell areas and perimeters)
        self.fe_file.write("\n")
        self.fe_file.write("EDGES \n")
        for k, v in self.edges.items():
            lambda_val = self.density_values[k]
            self.fe_file.write(f"{abs(k)}   {v[0]}   {v[1]}   density {lambda_val}\n")
            
        # Faces
        self.fe_file.write("\n")
        self.fe_file.write("FACES \n")
        for k, v in self.cells.items():
            str_value = " ".join(str(vv) for vv in v)
            self.fe_file.write(f"{abs(k)}   {str_value} \n")
            
        # Bodies
        self.fe_file.write("\n")
        self.fe_file.write("BODIES \n")
        for k, v in self.cells.items():
            self.fe_file.write(f"{abs(k)}   {k}\n")
        
        

        
        
        # Read commands
        self.fe_file.write("\n \n")
        self.fe_file.write("read \n \n")
        
        # Assign energies to cells
        self.fe_file.write("cell_id := 0;\n")
        self.fe_file.write("\n")
        self.fe_file.write("initialise_cell :=\n")
        self.fe_file.write("{\n")
        self.fe_file.write("\t" + "local command;\n")
        self.fe_file.write("\t" + 'command := sprintf "unset edges area_%g", cell_id;\n')
        self.fe_file.write("\t" + "exec command;\n")
        self.fe_file.write("\t" + 'command := sprintf "set facet[%g].edge method_instance area_%g", cell_id, cell_id;\n')
        self.fe_file.write("\t" + "exec command;\n")
        self.fe_file.write("\t" + 'command := sprintf "unset edges perimeter_%g", cell_id;\n')
        self.fe_file.write("\t" + "exec command;\n")
        self.fe_file.write("\t" + 'command := sprintf "set facet[%g].edge method_instance perimeter_%g", cell_id, cell_id;\n')
        self.fe_file.write("\t" + "exec command;\n")
        self.fe_file.write("};\n\n")
        
        
        self.fe_file.write("initialise_all_cells := \n")
        self.fe_file.write("{\n")
        self.fe_file.write("\t" + "foreach facet ff do\n")
        self.fe_file.write("\t" + "{\n")
        self.fe_file.write("\t\t" + "cell_id := ff.id;\n")
        self.fe_file.write("\t\t" + "initialise_cell;\n")
        self.fe_file.write("\t" + "}\n")
        self.fe_file.write("};\n\n")
        
        
        self.fe_file.write("show_all_edges off \n")
        # f.write("clipped on \n")
        self.fe_file.write("metric_conversion off \n")
        self.fe_file.write("autorecalc on \n")
        self.fe_file.write("gv_binary off \n")
        self.fe_file.write("gravity off \n")
        
        
        self.fe_file.write("initialise_all_cells; \n")
        
        self.fe_file.write("ii := 0; \n")

        if not self.polygonal:
            self.add_refining_triangulation(3)
        
        return self.fe_file
    