


## package
```shell
conda install
const 

```


## env


```shell
#  default: base
conda create -n foo
conda activate foo
conda install




```

anaconda.org
* defaults channels
    * main
    * R
    * msys2
    * conda-forge - is comminity maintained channel (replace anaconda defaults)


* Anaconda Distribution 
    * conda
    * NumPy
    * SciPy
    * pandas
* miniconda - not    
    * conda
* miniforge - default channel is conda-forge (commnity maintained miniconda replacement)
* manba - c++ implemented conda command (included in miniforge)

```shell
# disable auto init
conda config --set auto_activate_base false


manba create -n env_name
conda activate env_name
conda install pkg_name
```

```shell
conda create -n env_name -c conda-forge
conda install -c conda-forge pkg_name

```
    


```pytorch and cuda 

# from base , create new python 
conda create --name conda_py310  python=3.10
# To activate this environment, use                                                                                                                                                                                        
#
#     $ conda activate conda_py310
#
# To deactivate an active environment, use
#
#     $ conda deactivate

# install cuda toolkit 11.8
conda install cudatoolkit -c anaconda -y
nvidia-smi
# pytorch-cuda
conda install pytorch-cuda=12.1 -c pytorch -c nvidia -y
# other pytorch
conda install pytorch torchvision torchaudio -c pytorch -c nvidia -y  



# delete 
conda env list
conda env remove --name myenv
```

```python
import torch
torch.cuda.is_available()
```