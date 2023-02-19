from flask import Flask, render_template, request
from youtubevideo import print_channel_and_video_count, create_pdf
from youtubevideo import YouTubeVideo
import secrets
from jinja2 import Environment, FileSystemLoader
import boto3
import logging
import os

# set up the AWS credentials
aws_access_key_id = '<AWS_ACCESS_ID>'
aws_secret_access_key = '<AWS_ACCESS_KEY>'

app = Flask(__name__)

@app.route('/')
def index():
    #yt = YouTubeVideo()
    data = print_channel_and_video_count()
    return render_template('index.html', data=data)


@app.route('/', methods=['POST', 'GET'])
def video_id():
    video_url = request.form['video_id']
    video_id = video_url.split("v=")[1]
    youtube_video = YouTubeVideo(video_id)
    youtube_video.get_video_info()
    youtube_video.insert_into_database()

    #Process the video information as needed
    html = render_template('index.html', video_title=youtube_video.video_title,
                                          video_details=youtube_video.video_details,
                                          like_count=youtube_video.like_count,
                                          comment_count=youtube_video.comment_count, comments=youtube_video.comments)
    
    try:
        # Generate the PDF
        pdf = create_pdf(html)

        pdf_name = secrets.token_hex(5)
        file_name = (f"{pdf_name}.pdf")
        bucket_name = 'preetipdfs'

        # Save the PDF to a file
        with open(f"{pdf_name}.pdf", 'wb') as f:
            f.write(pdf)

        # #Upload PDF to S3 bucket
        s3 = boto3.resource('s3', region_name='us-east-2', api_version='2006-03-01', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        bucket = s3.Bucket (bucket_name)

        # Upload the file to S3
        s3.Object(bucket_name, file_name).put(Body=open(file_name, 'rb'))

        os.remove(file_name)

        url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

        logging.info(f"File has been uploaded to S3 {url}")
    
    except Exception as e:
        logging.error(f"Failed to create or upload PDF {e}")
    
    
    return html


if __name__ == '__main__':
    app.run(debug=True)