import os

from pyexp.campaign import Campaign
from pyexp.runner import SimpleRunner


def main():
    script = ["python3", os.path.abspath('script.py')]
    # script = ["python3"]-c \"print('hello')\""]
    campaign_dir = "campaigns/experiment"
    default_params = {
        "name": None,
    }

    campaign = Campaign.new(script, campaign_dir, default_params, overwrite=True)

    configs = {"name": ["alberto", "bruno"]}

    runner = SimpleRunner()

    campaign.run_missing_simulations(runner, configs)


if __name__ == "__main__":
    main()
