import re
import numpy as np

def read_1D_input(
        file_name : str,
        var_dict = {
            'x' : ['x_end', 'y_end', 'z_end'], 
            'edge_index' : ['PareID', 'ID'], 
            'edge_attr' : ['Length', 'Diameter', 'Gene', 'Lobe', 'Vol1-0']
        }
    ):
    r"""Read Output_subject_Amount_St_whole.dat
    Data format
    ID PareID Length Diameter ... Vol1-0 Vol0 Vol1
    -  -      -      -        ... -      -    -
    -  -      -      -        ... -      -    -
    (---------information of ith branch----------)
    -  -      -      -        ... -      -    -
    """
    def _float(str):
        _dict = {'C':0, 'P':0, 'E':0, 'G':0, 'T':1}
        try:
            return float(str)
        except:
            return _dict[str]
    _vectorized_float = np.vectorize(_float)

    file = open(file_name, 'r')
    # Read header
    header = file.readline()
    # Read data
    data = file.read()
    # Done reading file
    file.close()

    # Process header
    vars = header.replace('\n',' ')
    vars = vars.split(' ')
    vars = list(filter(None, vars))

    n_var = len(vars)

    # Process data
    data = data.replace('\n',' ')
    data = data.split(' ')
    data = list(filter(None, data))

    data = np.array(data).reshape((-1, n_var)).transpose()
    data_dict = {}
    for i in range(len(vars)):
        data_dict[vars[i]] = _vectorized_float(data[i])
    
    # Rearange data
    data_dict['x_end'] = np.insert(data_dict['x_end'], 0, data_dict['x_start'][0])
    data_dict['y_end'] = np.insert(data_dict['y_end'], 0, data_dict['y_start'][0])
    data_dict['z_end'] = np.insert(data_dict['z_end'], 0, data_dict['z_start'][0])

    out_dict = {}
    for var in var_dict:
        out_dict[var] = []
        for data_var in var_dict[var]:
            out_dict[var].append(data_dict[data_var])

    out_dict['x'] = np.array(out_dict['x'], dtype=np.float32).transpose()
    out_dict['edge_index'] = np.array(out_dict['edge_index'], dtype=np.int32)
    out_dict['edge_attr'] = np.array(out_dict['edge_attr'], dtype=np.float32)
    return out_dict

def read_1D_output(
        file_names,
        var_dict = {
            'pressure' : 'p',
            'flowrate' : 'flowrate'
        }
    ):
    r"""Read data_plt_nd/plt_nd_000time.dat (all time_id)
    Data format
    VARIABLES="x" "y" "z" "p" ... "flowrate"  "resist" "area"                                    
     ZONE T= "plt_nd_000time.dat                                 "
     N=       xxxxx , E=       xxxxx ,F=FEPoint,ET=LINESEG
    -  -      -      -        ... -      -    -
    -  -      -      -        ... -      -    -
    (---------information of ith node----------)
    -  -      -      -        ... -      -    -
    -  -
    -  -
    (---------connectivity of jth branch-------)
    -  -
    """
    # Read variable list and n_node, n_edge
    file = open(file_names[0], 'r')
    line = file.readline()
    line = line.replace('VARIABLES',' ')
    line = line.replace('=',' ')
    line = line.replace('\n',' ')
    line = line.replace('"',' ')
    vars = list(filter(None, line.split(' ')))
    n_var = len(vars)

    file.readline()
    line = file.readline()
    line = line.split(',')
    n_node = int(line[0].replace('N=',' ').replace(' ',''))
    n_edge = int(line[1].replace('E=',' ').replace(' ',''))
    file.close()

    out_dict = {}
    for var in var_dict:
        out_dict[var] = []
    # Read all time id
    for file_name in file_names:
        # Skip header and read data part
        file = open(file_name,'r')
        file.readline()
        file.readline()
        file.readline()
        data = file.read()
        file.close()

        # Process data string into numpy array of shape=(n_node, n_var)
        data = data.replace('\n',' ')
        data = list(filter(None, data.split(' ')))
        edge_index = data[n_var*n_node:n_var*n_node + 2 * n_edge]
        data = np.array(data[0:n_var*n_node], dtype=np.float32)
        data = data.reshape((n_node, n_var)).transpose()
        
        # Store to variable dict
        for var in var_dict:
            out_dict[var].append(np.expand_dims(data[vars.index(var_dict[var])], axis=-1))
        
    # Aggregate results from all time id.
    for var in var_dict:
        out_dict[var] = np.concatenate(out_dict[var], axis=-1)
    edge_index = np.array(edge_index, dtype = np.int32).reshape((n_edge, 2)).transpose() - 1
    if out_dict['flowrate'] is not None:
        out_dict['flowrate'] = node_to_edge(out_dict['flowrate'], edge_index)
    return out_dict

def node_to_edge(node_attr, edge_index):
    return np.array([node_attr[i] for i in edge_index[1]])
        

if __name__ == '__main__':
    time_id = [str(i).zfill(3) for i in range(201)]
    file_names = [f'/data1/tam/datasets/10081/CFD_1D/data_plt_nd/plt_nd_000{i}.dat' for i in time_id]
    data = read_1D_output(
        file_names=file_names
    )
    print(data)