# tonkotsu_cop_bot
A reddit bot for spreading awareness of the misspelling of "tonkotsu".

`bayes.py`: Learn a multinomial naive bayes model trained on a bag-of-words from submission titles.

`bot.py`: Interact with reddit to get titles, use model created by `bayes.py` to predict if title has "tonkatsu" typo, comment if so.

`test-bot.py`: Test suite for `bot.py`.

## `bayes.py`
```
$ python bayes.py -h
usage: bayes.py [-h] [-d FILE] [-o FILE] [-t FILE] [-s FLOAT]

Generate bayesian model for tonkatsu

optional arguments:
  -h, --help            show this help message and exit
  -d FILE, --data FILE  Labeled data file (default: data/all_labeled_data.txt)
  -o FILE, --out FILE   Name of model output (pickle) (default:
                        data/model.pkl)
  -t FILE, --test_out FILE
                        Test data output file (default: data/test_data.txt)
  -s FLOAT, --test_split FLOAT
                        Test data split ratio (default: 0.2)
 ```

Contents of `data/all_labelled_data.txt` (`--data`) were produced by using Google search in /r/ramen, /r/food, and /r/foodporn to find instances of the word "tonkatsu" in submission titles. A label was assigned manually to indicate if "tonkatsu" was the right spelling (`0`), or if "tonkotsu" is what the user meant (`1`).

These entries are split into training and testing data (`--test_split`). The training data is fed into a scikit-learn `CountVectorizer`, and that fitted `CountVectorizer` is kept for reuse on the test data set.

The vectorized titles are used to train a multinomial naïve bayes model.

Model is used to predict a label of the title containing "tonkatsu" - `1`: mistake spelling, `0`: correct spelling.

Test data are vectorized using the same `CountVectorizer`, the model is tested, and a confusion matrix is produced.

Test data true values, predicted values, and original title strings are stored in a .txt file (`--test_out`) for use in testing.

Finally, a pickle (`--out`) is produced containing the model, the test data (including true labels), prediction accuracy, and the `CountVectorizer`. The inclusion of test data and accuracy allows for performance consistency assessment when the model is imported for use in `bot.py`.


## `bot.py`
```
$ python bot.py -h
usage: bot.py [-h] [-c FILE] [-D] [-d FILE] [-l FILE] [-m PKL] [-p FILE]

Run the Tonkotsu Police Bot

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --comment FILE
                        Bot comment string file (default: data/comment.txt)
  -D, --Debug           Debugging flag (default: False)
  -d FILE, --deleted FILE
                        Deleted comments file (default: data/deleted.txt)
  -l FILE, --log FILE   Log file (default: data/.log)
  -m PKL, --model PKL   Model for classifying titles (default: data/model.pkl)
  -p FILE, --posts FILE
                        Previously commented posts file (default:
                        data/id_file.txt)
```

`PRAW` is used to create a reddit instance, signing the bot in using the info of the local `config.py` file.

The bot looks at the newest posts in the subreddits of interest, and hits on those containing the string "tonkatsu" (case insensitive). If the post has not been assessed before (as indicated by the presence of the post ID in `--posts`), then the previously trained model (`--model`) is used to assign a label/prediction to the post title.

If the model predicts mistake spelling, a comment (`--comment`) is posted. If the model predicts non-mistake spelling, no comment is posted. The bot then sends a message to itself and a "human" overseer account describing its choice of action. 

Whether or not the model predicted mistake spelling, the post ID and title string are recorded in `--posts`.

Next, the bot checks its previous comments' statuses. If they have been downvoted too many times, the comment is deleted, and messages are sent. The comment ID is recorded in `--deleted` for later reference.

During the above steps, logging takes place. By default, only `logging.info` is used, but `logging.debug` may be activated with `--debug` for more thorough logging to the `--log` file.

Running of the bot is accomplished with CRON instead of continuously running the script and utilizing `submission.stream()` in PRAW. This is to avoid known issues related to that function's inability to handle exceptions and continue or restart the stream.
