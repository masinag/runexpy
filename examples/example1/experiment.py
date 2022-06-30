import json
import os

import approx_pi
import matplotlib.pyplot as plt

from pyexp.campaign import Campaign
from pyexp.runner import SimpleRunner
from pyexp.utils import DefaultParamsT, IterParamsT


def main():
    script = ["python3", os.path.abspath("approx_pi.py")]
    # script = ["python3"]-c \"print('hello')\""]
    campaign_dir = "campaigns/experiment"
    default_params: DefaultParamsT = {
        "seed": None,  # param without a default value
        "n": approx_pi.DEFAULT_N,  # also default params must be specified
    }

    campaign = Campaign.new(script, campaign_dir, default_params, overwrite=True)

    configs: IterParamsT = {
        "seed": [1, 2, 3, 4],  # non-default params must be set
    }

    runner = SimpleRunner()

    campaign.run_missing_experiments(runner, configs)

    results = campaign.get_results_for(configs)

    for result, files in results:
        with open(files[approx_pi.OUT_FILE], "r") as f:
            data = json.load(f)
            print(f"Seed: {result.params['seed']} -> {data['pi_value']}")
            img_name = f"plot_{result.params['seed']}_{result.params['n']}"
            # draw circle
            _, axes = plt.subplots()
            cc = plt.Circle((0.5, 0.5), 0.5, alpha=0.5, color='r')
            axes.set_aspect(1)
            axes.add_artist(cc)
            # draw points
            xx, yy = data["draws"]
            plt.scatter(xx, yy, s=1)
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            print(f"Saving {img_name}")
            plt.savefig(img_name)
            plt.clf()


if __name__ == "__main__":
    main()
