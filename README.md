# opening-hours

Opening hours is a python library and command-line program for formatting
opening hours JSON to a human readable format.

Requirements:

- Python 2.7 or 3.5
- voluptuous python library if using schema validation

For example the following JSON:

```json
{
    "tuesday": [
        {
            "type": "open",
             "value": 36000
        },
        {
            "type": "close",
            "value": 64800
        }
    ]
}
```

Would result in the following output

```
Monday: Closed
Tuesday: 10 am - 6 pm
Wednesday: Closed
Thursday: Closed
Friday: Closed
Saturday: Closed
Sunday: Closed
```

## Command line usage

```
usage: opening_hours.py [-h] [--validate] filename

positional arguments:
  filename    the filename of the JSON file from where the opening hours are
              read

optional arguments:
  -h, --help  show this help message and exit
  --validate  validate the opening hours data
```

## Running the supplied example with validation

    $ virtualenv env
    $ . ./env/bin/activate
    $ pip install -r requirements.txt
    $ python opening_hours.py --validate data.json

## Running doctests

    $ python -m doctest -v opening_hours.py
