# science-revisioning
Revision matching to author-reviewer discussions in scientific papers.

In openreview.net papers can be peer-reviewed. We try to match the review suggestions with the respective change that was made in the paper.

# How
1. Paper revisions and reviews are crawled from openreview.net
2. The paper is parsed into structured data using science-parse
3. The revisions are diff'ed and matched to the review that suggested that change. Matching is currently done by using the time stemp.

# How to use it
1. Run a science-parser server (see [science-parse server](https://github.com/allenai/science-parse/blob/master/server/README.md))
2. execute jupyter-notebook TODO

# Future Work
- Refine matching, by using e.g. keywords or more sophisticated NLP analysis
- Split the reviews into single proposed changes
