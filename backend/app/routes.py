from flask import Flask, render_template, request
import json
from productionist import Productionist, ContentRequest


CONTENT_BUNDLE_NAME = 'test'
app = Flask(__name__)
debug = True


@app.route('/')
def home():
    """Render the default page for the web app."""

    return render_template('app.html', random_output='')


@app.route('/contentRequest', methods=['POST'])
def satisfy_content_request():
    """Furnish generated content that satisfies an author-defined content request."""
    # Receive the raw content request (as JSON data)
    data = request.data
    print "YOOOOOO"
    print data
    print "END TRANSMISSION"
    # Parse the raw JSON into a dictionary
    content_request = json.loads(data)
    # Grab out everything we need to send to Productionist
    required_tags = {tag["name"] for tag in content_request["tags"] if tag["status"] == "required"}
    prohibited_tags = {tag["name"] for tag in content_request["tags"] if tag["status"] == "disabled"}
    scoring_metric = [
        (tag["name"], int(tag["desirability"])) for tag in content_request["tags"] if tag["status"] == "enabled"
    ]
    # Time to generate content; prepare the actual ContentRequest object that Productionist will process
    content_request = ContentRequest(
        must_have=required_tags, must_not_have=prohibited_tags, scoring_metric=scoring_metric
    )
    print "\n-- Attempting to fulfill the following content request:\n{}".format(content_request)
    # Fulfill the content request to generate N outputs (each being an object of the class productionist.Output)
    output = app.productionist.fulfill_content_request(content_request=content_request)
    if output:
        print "\n\n-- Successfully fulfilled the content request!"
        # Send the generated outputs back to the authoring tool as a single JSON package
        output_as_json_package = json.dumps(output.payload)
        print output_as_json_package
        return output_as_json_package
    print "\n\n-- The content request cannot be satisfied by the content bundle."
    return "The content request cannot be satisfied by the content bundle."


if __name__ == '__main__':
    # Start up the app!
    app.productionist = Productionist(
        content_bundle_name=CONTENT_BUNDLE_NAME,
        content_bundle_directory='./static',
        probabilistic_mode=False,
        repetition_penalty_mode=False,
        terse_mode=False,
        verbosity=0,
        seed=None
    )
    app.debug = debug
    app.run()
