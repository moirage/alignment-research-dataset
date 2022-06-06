# AI Alignment Research Dataset
A dataset of alignment research and code to reproduce it. You can download version 1.0 of the dataset [here](https://drive.google.com/file/d/13SM1gADKqk-lvHu7Vhwe_Aiw-TyXy3LQ/view?usp=sharing).

## Sources

Below, you can find a table of the number of texts in the dataset grouped into various sources. The table is up-to-date with version 1.0 of the dataset (June 4th, 2022).

<img src="./imgs/dataset_sources.PNG" alt="dataset_sources.PNG" width=600 />

## Development Environment

To set up the development environment, run the following steps:

```bash
git clone https://github.com/moirage/alignment-research-dataset
cd alignment-research-dataset
pip install -r requirements.txt
```
You will also need do install [grobid](https://github.com/kermitt2/grobid) on your machine to run some of the scripts. There is some documentation [here](https://grobid.readthedocs.io/en/latest/Install-Grobid/) on how to install it. Make sure to put the grobid config file in the root of your repository.

## Contributing

Join us on EleutherAI's [discord server](https://discord.com/invite/zBGx3azzUn) in the #accelerating-alignment channel. We are looking for people who want to contribute by adding more AI alignment text to the dataset as well as clean the data. 

We are currently cleaning audio transcripts that have been created using speech-to-text software, if you would like to contribute, please let us know. We are also hoping to categorize the AI alignment videos in ways that are useful for newcomers. Some initial ideas include useful search tags like required background, topic, how good the content is, and if it's a lecture or conversation.

## Citing the Dataset

Please use the following citation when using our dataset:

Kirchner, J. H., Smith, L., Thibodeau, J., McDonnell, K., and Reynolds, L. "Understanding AI alignment research: A Systematic Analysis." arXiv preprint arXiv:2022.4338861 (2022).
