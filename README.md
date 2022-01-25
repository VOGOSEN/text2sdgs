# text2sdgs : simple SDG text classifier

This is a simple N-Gram NLP model that outputs the [Sustainable Development Goals](https://sdgs.un.org/goals) related to a given text.

# How it works?

* N-grams and their frequencies are extracted from the input text. The number of grams can be specified by the user.
* N-grams are mapped to SDG concepts.
* A relevance score is computed based on the frequencies and the length of the grams. This relevance score can be adjusted by the user.

## Data source

This project uses OSDG.ai open data [osdg-tool](https://osdg.ai/). Users can also easily format and input their own data.

## Learn more

[Vogosen Free Tools](https://vogosen.com/tool)

License
----
MIT
