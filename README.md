# runexpy - Experiment manager
Python library to perform multiple executions of a script with different parameters,
manage the results and collect them.

## How does it work?

### Get you script
Write a script (it can be a Python program or any command line executable) which can take
command line parameters in GNU standard, i.e. in the format `--arg=value`.

The script can print anything on standard output and standard error. Moreover, it can 
produce any file in the current working directory, e.g. `output.txt` can contain the 
result computed by the script.

Example of a Python script, e.g. `script.py`
```python
import random
from argparse import ArgumentParser


def main():
    ap = ArgumentParser("Draw a random number")
    ap.add_argument("--seed", "-s", type=int, required=True)
    ap.add_argument("--lower", "-l", type=float, default=0)
    ap.add_argument("--upper", "-u", type=float, default=1)
    args = ap.parse_args()

    random.seed(args.seed)
    draw = args.lower + random.random() * (args.upper - args.lower)
    with open("output.txt", "w") as f:
        f.write(str(draw))


if __name__ == "__main__":
    main()
```

### Define you experimental settings
Write a Python script that defines the experiments you want to run.

Example, e.g. experiment.py
```python
from runexpy.campaign import Campaign
from runexpy.runner import SimpleRunner


def main():
    # for a python script
    script = ["python3", "script.py"]
    # for any command-line executable
    # script = "my-program"

    campaign_dir = "campaigns"

    # define the arguments with their default value if any, else None
    default_params = {
        "seed": None,
        "lower": 0,
        "upper": 1,
    }

    c = Campaign.new(script, campaign_dir, default_params)

    runs = {
        "seed": [0, 1, 2],
        "lower": [0, 0.5],
    }
    # equivalent to
    # runs = [
    #     {"seed": 0, "lower": 0,   "upper": 1},
    #     {"seed": 0, "lower": 0.5, "upper": 1},
    #     {"seed": 1, "lower": 0,   "upper": 1},
    #     {"seed": 1, "lower": 0.5, "upper": 1},
    #     {"seed": 2, "lower": 0,   "upper": 1},
    #     {"seed": 2, "lower": 0.5, "upper": 1},
    # ]

    # run the experiments
    runner = SimpleRunner()
    c.run_missing_experiments(runner, runs)

    # parse results
    for result, files in c.get_results_for(runs):
        with open(files["output.txt"]) as f:
            draw = f.read()
        print(
            f"Draw in interval [{result.params['lower']}, {result.params['upper']}]"
            f" with seed {result.params['seed']}: {draw}"
        )
        # print("stdout: ", open(files["stdout"]).read())
        # print("stderr: ", open(files["stderr"]).read())


if __name__ == "__main__":
    main()
```

### Run your experiments
By running your `experiment.py`, runexpy will create a directory containing all your experiments
with the corresponding results and files produced. A database is kept to store all the informations
and allow for an easy retrival of the outputs.
