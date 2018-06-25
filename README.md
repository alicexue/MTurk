# Web App to Run Studies on Amazon Mechanical Turk

One study is up and running [here](http://calkins.psych.columbia.edu/MDMMT).

This web app uses the Flask framework. All of the middleware is in python. 

Studies are run in the browser with Javascript. HTML canvases are used to display images while svg elements are used for text and interactive components. 

Data files are stored using python pandas as csv files.

## References
Javascript references:
[Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

Flask references:
[Flask blueprints](http://flask.pocoo.org/docs/1.0/blueprints/) and [structure](http://exploreflask.readthedocs.io/en/latest/blueprints.html#where-do-you-put-them)

MTurk references:
[MTurk Concepts](https://docs.aws.amazon.com/AWSMechTurk/latest/RequesterUI/mechanical-turk-concepts.html),
[AWS MTurk Commands](https://docs.aws.amazon.com/cli/latest/reference/mturk/index.html#cli-aws-mturk),
[FAQ](https://requester.mturk.com/help/faq),
[HIT Lifecycle](https://blog.mturk.com/overview-lifecycle-of-a-hit-e6956b4f3bb1)

Other MTurk references:
[Code samples for creating external HIT](https://github.com/aws-samples/mturk-code-samples)

See [MTurk_Web_App_Guide.pdf](https://github.com/alicexue/MTurk/blob/master/MTurk_Web_App_Guide.pdf) for more details. (Download the file to have access to the web links)
