
# Auto-Optimizer

## Project Description
This program helps speed up the process of tuning .dat files for High Performance Linpack.
It achieves this by generating many files to run on the target system, runs them program,
reads bach the data and displays it to the screen allowing a user to quickly view optimal
parameters




## Run Locally

Clone the project

```bash
  git clone https://github.com/DUSCC/Auto-Optimizer.git
```

Install requirements

```bash
  pip install -r requirements.txt
```

Run main.py

```bash
  python main.py
```


## Usage/Examples

### Setting up configs

To run the optimization you need to first connect to a server. for ease of use, this is done using saved configs. To create a new config, click the 'Host Config' button in the SSH menu dropdown

#### Sample config

    |       HOST        | USER   | PORT |
    |hamilton8.dur.ac.uk| pzhm13 |  22  |

    by default SSH will run through port 22

### Connecting to a server

Once you have saved a config you want to use (host, user, port), you can connect with it. click the 'Connect to Host' button in the SSH menu dropdown

### Setting up search parameters

In order for the program to run, you must set up the range you wish to sample over, and the number of samples per variable i.e. the field (NB min, NB max, NB n) correspond to minimum NB to be used, Maximum NB to be used and the number of samples to take in the range.



## Trouble shooting
--- Work In Progress ---
## Roadmap

- General bugfixes

- Predicted Completion Percent to give indication of analysis completion

- Allow the program to create more complicated .dat files by default to speed up execution time (at the moment #N, #NBs, #Grids ect are all set to 1)

- Analyze a wider range of variables (currently supported -> NBs & (Ps,Qs)

- Allow different compilers and Linear Algebra Libraries i.e. (gcc, llvm, aocc, aocl, blis) to be built and used from the program






## Contributing

Contributions are always welcome!

At the moment this project follows no specific style, there will be an effort made to standardize the old code. future contributions should follow the PEP 8 style guide. care should be taken to use well named variable and functions as well as any neccesary docstrings and comments for other users.

To contribute, fork the repo (with a descriptive name) and clone it. once the fork is stable, you can request a merge with the master branch. DO NOT work directly on the master branch unless you have a good reason to.

