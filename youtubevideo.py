import googleapiclient.discovery
import mysql.connector
import logging
import pdfkit
import os

def create_pdf(html):
    # Set the path to the wkhtmltopdf executable
    
    #path_wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"

    path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
    
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Generate a PDF from the HTML
    pdf = pdfkit.from_string(html, False, configuration=config)

    return pdf


logging.basicConfig(filename='youtube.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def print_channel_and_video_count():
        try:
            youtube_videos = [
                {'channel_id': 'UCNU_lfiiWBdtULKOw6X0Dig', 'channel_name': 'Krish Naik'},
                {'channel_id': 'UCb1GdqUqArXMQ3RS86lqqOw', 'channel_name': 'iNeuron'},
                {'channel_id': 'UCDrf0V4fcBr5FlCtKwvpfwA', 'channel_name': 'College Wallah'}
            ]

            developer_key = "<DEVLOPER_KEY>"
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=developer_key)

            data = []
            for video in youtube_videos:
                request = youtube.channels().list(
                    part="statistics",
                    id=video['channel_id']
                )
                response = request.execute()
                video_count = response['items'][0]['statistics']['videoCount']
                data.append({'channel_name': video['channel_name'], 'video_count': video_count})
                #print(f"Channel Name: {video['channel_name']}")
                #print(f"Video Count: {video_count}")
                #print("-" * 20)
            return data
        except Exception as e:
            logging.error(f"An error occurred while fetching video count info: {str(e)}")


class YouTubeVideo:
    def __init__(self, video_id):
        self.video_id = video_id
        self.developer_key = "<DEVELOPER_KEY>"
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=self.developer_key)
        self.channel_name = None
        self.video_title = None
        self.video_details = None
        self.like_count = None
        self.comment_count = None
        self.comments = []
        self.author_name = None
        self.video_count = None


    def get_channel_info(self, channel_id):
        try:
            request = self.youtube.channels().list(
                part="snippet, statistics",
                id=channel_id
            )
            response = request.execute()
            self.channel_name = response["items"][0]["snippet"]["title"]
            self.video_count = response["items"][0]["statistics"]["videoCount"]
        
        # except HttpError as e:
        #     logging.error(f'An HTTP error occurred: {e}')
        except KeyError as e:
            logging.error(f'A key error occurred: {e}')
        except Exception as e:
            logging.error(f"An error occurred while fetching channel info: {e}")
    

    def get_video_info(self):
        """
        Retrieve information about a video using the YouTube Data API.

        Args:
            api_key (str): The API key for accessing the YouTube Data API.
            video_id (str): The ID of the YouTube video.

        Returns:
            A dictionary containing information about the video, including its ID, title, description, channel name, and
            publication date.
        """
        try:
            request = self.youtube.videos().list(
                part="snippet, statistics",
                id=self.video_id
            )
            response = request.execute()
            self.video_title = response["items"][0]["snippet"]["title"]
            self.video_details = response["items"][0]["snippet"]["description"]
            self.like_count = response["items"][0]["statistics"]["likeCount"]
            self.comment_count = response["items"][0]["statistics"]["commentCount"]

            # Get the person name who posted the video
            channel_id = response["items"][0]["snippet"]["channelId"]
            self.get_channel_info(channel_id)

            # Get the video comments
            comments = []
            results = self.youtube.commentThreads().list(
                part="snippet",
                videoId=self.video_id,
                textFormat="plainText"
            ).execute()
            
            
            for item in results["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                author_name = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                comments.append((comment, author_name))
                #comments.append(author_name)
            self.comments = comments
        
        # except HttpError as e:
        #     logging.error(f'An HTTP error {e.resp.status} occurred: {e.content}')

        except Exception as e:
            logging.error(f'An error occurred while fetching video info: {str(e)}')

    def insert_into_database(self):
        try:
            # Insert the video data into MySQL
            cnx = mysql.connector.connect(
                user='<USER>',
                password='<PASSWORD>',
                host='<HOST>',
                database='<DB_NAME>'
            )
            cursor = cnx.cursor()

            add_video = ("INSERT INTO videos "
                        "(video_id, video_title, video_details, like_count, comment_count, channel_name) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
            data_video = (self.video_id, self.video_title, self.video_details, self.like_count, self.comment_count, self.channel_name)
            cursor.execute(add_video, data_video)

            # Insert the comments data into MySQL
            for comment in self.comments:
                add_comment = ("INSERT INTO comments "
                            "(comment_text, author_name, video_title, video_id) "
                            "VALUES (%s, %s, %s, %s)")
                data_comment = (comment[0], comment[1], self.video_title, self.video_id)
                cursor.execute(add_comment, data_comment)

            cnx.commit()
            cursor.close()
            cnx.close()
            logging.info("Video data and comments inserted into the database.")

        except mysql.connector.Error as error:
            logging.error(f"Failed to insert data into MySQL: {error}")
            raise
        
        except Exception as e:
            logging.error(f"Failed to add data into Database: {e}")
            raise


    def print_video_info(self):
        try:
            print("Video title:", self.video_title)
            print("Video details:", self.video_details)
            print("Number of likes:", self.like_count)
            print("Number of comments:", self.comment_count)
            print("Channel name:", self.channel_name)
        except Exception as e:
            logging.error("Failed to display Video info: ", {str(e)}) 

    def print_video_comments(self):
        try:
            for comment in self.comments:
                print(comment)
        except Exception as e:
            logging.error("Failed to display comments: ", {str(e)})


if __name__ == '__main__':
    try:
        # Get the video ID from the user
        video_url = input("Enter the YouTube video URL: ")
        video_id = video_url.split("v=")[1]

        # Get the video info
        video = YouTubeVideo(video_id)
        video.get_video_info()

        # Print Channel Names and Video Count for iNeuron, College Wallah and Krish Naik        
        #video.print_channel_and_video_count()

        # Insert the data into MySQL
        video.insert_into_database()

        # Print the data for verification
        #video.print_video_info()

        # Print the person name who posted the video along with each comment
        #video.print_video_comments()

    except googleapiclient.errors.HttpError as e:
        print("An HTTP error occurred: ", str(e))
    except mysql.connector.Error as e:
        print("A database error occurred: ", str(e))

    except Exception as e:
        print("An error occurred: ", str(e))
