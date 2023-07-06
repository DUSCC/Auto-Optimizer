
# Auto-Optimizer

## Project Description
This program helps speed up the process of tuning .dat files for High Performance Linpack.
It achieves this by generating many files to run on the target system, runs them program,
reads bach the data and displays it to the screen allowing a user to quickly view optimal
parameters




## Roadmap

- General bugfixes

- Predicted Completion Percent to give indication of analysis completion

- Allow the program to create more complicated .dat files by default to speed up execution time (at the moment #N, #NBs, #Grids ect are all set to 1)

- Analyze a wider range of variables (currently supported -> NBs & (Ps,Qs)

- Allow different compilers and Linear Algebra Libraries i.e. (gcc, llvm, aocc, aocl, blis) to be built and used from the program






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

To run the optimization you need to first connect to a server. for ease of use, this is done using saved configs. To create a new config, click the Host Config button in the SSH menu dropdown

