import os
import numpy as np
import torch
from torch_geometric.data import Dataset, InMemoryDataset
from data.data import TorchGraphData
from typing import Optional, Callable, Union, List, Tuple
from data.file_reader import *


class DatasetLoader(Dataset):
    r"""Base dataset loader class for graph data
    Loader is specifically used for loading a processed dataset.
    Function 'process()' is not implemented.
    """
    def __init__(self, 
        root_dir: Optional[str] = None, 
        data_names: Optional[Union[str, List[str], Tuple]] = 'all',
        transform: Optional[Callable] = None, 
        pre_transform: Optional[Callable] = None, 
        pre_filter: Optional[Callable] = None
    ):
        self._data_names = data_names
        super().__init__(root_dir, transform, pre_transform, pre_filter)
    
    @property
    def data_names(self) -> Union[List[str], Tuple]:
        if self._data_names == 'all':
            data_dir = self.root + '/processed/'
            data_names = os.listdir(data_dir)
            _filter = lambda s : not s in ['pre_filter.pt', 'pre_transform.pt']
            data_names = list(filter(_filter, data_names))
            return [data.replace('.pt','',data.count('.pt')) for data in data_names]
        else:
            return self._data_names

    @property
    def processed_file_names(self) -> Union[List[str], Tuple]:
        return [self.root+'/processed/'+data+'.pt' 
                                for data in self.data_names]

    def process(self):
        pass
    
    def len(self):
        return len(self.data_names)

    def __getitem__(self, index):
        return torch.load(self.processed_file_names[index])



class DatasetBuilder(Dataset):
    r"""Base dataset builder class for graph data
    Builder is specifically used for read/process/save graph dataset. 
    """
    def __init__(self,
        raw_dir: Optional[str] = None,
        root_dir: Optional[str] = None,
        data_names: Optional[Union[str, List[str], Tuple]] = 'all',
    ):
        # No transforming for builder class.
        transform = None
        pre_transform = None
        pre_filter = None
        self.raw = raw_dir
        self._data_names = data_names
        super().__init__(root_dir, transform, pre_transform, pre_filter)
    
    @property
    def data_names(self) -> Union[List[str], Tuple]:
        raise NotImplemented

    def process(self):
        # Write code for data processing here.
        raise NotImplemented




class OneDDatasetBuilder(DatasetBuilder):
    r"""Constructing OneD dataset
    """

    def __init__(self, 
        raw_dir: Optional[str] = None, 
        root_dir: Optional[str] = None, 
        data_names: Optional[Union[str, List[str], Tuple]] = 'all',
        time_id: List[str] = None
    ):
        self.time_id = time_id
        super().__init__(raw_dir, root_dir, data_names)

    @property
    def data_names(self) -> Union[List[str], Tuple]:
        if self._data_names == 'all':
            data_dir = self.raw
            data_names = os.listdir(data_dir)
            # _filter = lambda s : os.path.isdir(self.raw + s)
            # data_names = list(filter(_filter, data_names))
            return data_names
        else:
            return self._data_names
    
    @property
    def processed_file_names(self) -> Union[List[str], Tuple]:
        return [self.root+'/processed/'+data+'.pt' 
                                for data in self.data_names]

    def process(self):

        # Output_subject_Amout_St_whole.dat
        file_name_input = lambda subject : self.raw+'/'+subject+\
            '/CFD_1D/Output_'+subject+'_Amount_St_whole.dat'
        # data_plt_nd/plt_nd_000time.dat
        file_name_output = lambda subject, time : self.raw+'/'+subject+\
            '/CFD_1D/data_plt_nd/plt_nd_000'+time+'.dat'
        for subject in self.data_names:
            print(f'Process subject number {self.data_names.index(subject)}, subject name : {subject}.')
            data_dict_input = read_1D_input(file_name_input(subject))
            file_names_output = [file_name_output(subject, time) for time in self.time_id]
            data_dict_output = read_1D_output(file_names_output)
            data = TorchGraphData(
                x = torch.tensor(data_dict_input['x']).type(torch.float32),
                edge_index = torch.tensor(data_dict_input['edge_index']).type(torch.LongTensor),
                edge_attr = torch.tensor(data_dict_input['edge_attr']).type(torch.float32),
                pressure = torch.tensor(data_dict_output['pressure']).type(torch.float32),
                flowrate = torch.tensor(data_dict_output['flowrate']).type(torch.float32)
            )
            torch.save(data, self.processed_file_names[self.data_names.index(subject)])