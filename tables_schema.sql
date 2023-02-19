-- Create Database named youtube
CREATE DATABASE youtube;

-- Create a table to store Video information
CREATE TABLE videos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  video_id VARCHAR(50),
  video_title VARCHAR(255),
  video_details TEXT,
  like_count INT,
  comment_count INT,
  channel_name VARCHAR(255)
);

-- Create index on the videos table that is referenced by the foreign key in the comments table
CREATE INDEX idx_videos_video_id ON videos (video_id);

-- Create a table to store comments
CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  comment_text TEXT,
  author_name VARCHAR(255),
  video_id VARCHAR(50),
  video_title VARCHAR(150),
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);
