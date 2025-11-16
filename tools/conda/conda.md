


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
manba create -n env_name
conda activate env_name
conda install pkg_name
```

```shell
conda create -n env_name -c conda-forge
conda install -c conda-forge pkg_name

```
    
