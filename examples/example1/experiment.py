from pyexp.campaign import Campaign
from pyexp.runner import SimpleRunner


def main():
    script = "python3 script.py"
    campaign_dir = "campaigns/experiment"
    default_params = {
        "name": None,
    }

    campaign = Campaign.new(script, campaign_dir, default_params)

    configs = {"name": ["alberto", "bruno"]}

    runner = SimpleRunner()

    campaign.run_missing_simulations(runner, configs)


if __name__ == "__main__":
    main()
