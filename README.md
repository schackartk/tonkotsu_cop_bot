# tonkotsu_cop_bot
A reddit bot for spreading awareness of the misspelling of "tonkotsu".

`bayes.py`: Learn a multinomial naive bayes model trained on a bag-of-words from submission titles.

`bot.py`: Interact with reddit to get titles, use model created by `bayes.py` to predict if title has "tonkatsu" typo, comment if so.

`test-bot.py`: Test suite for `bot.py`.
