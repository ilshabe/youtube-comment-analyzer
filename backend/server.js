const express = require('express');
const { Innertube } = require('youtubei.js');
const fs = require('fs');

const app = express();
const port = 3000; // Or any port you prefer

// Cookie string extracted from the user's provided JSON
const cookieString = "PREF=f4=4000000&f6=40000000&tz=Europe.Moscow&f7=100&f5=20000; HSID=AzIts3EOJ8M_Q72rd; SSID=AwS26jNssxnqWMjv2; APISID=lKbFNr8-gEjQigyh/AbryCn3EZKmvFUYgd; SAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; __Secure-1PAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; __Secure-3PAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; SID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlNUX5ab5WrJ8clM_lHg9KQ3wACgYKAXASARESFQHGX2Mi8zhJ89vsBxFLJiBRXf6xNBoVAUF8yKqVOoyjzKAqBZO_r-dHlNfv0076; __Secure-1PSID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlN8bKdDZ0HsyGZvNugHa6SjAACgYKAaMSARESFQHGX2Midsz_tu_lI2VHVU1-_Mdo8hoVAUF8yKqY-ZFNI6xB8HDbJQNaakgU0076; __Secure-3PSID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlNSeaU4OJpzEaEkEHsUgnUDAACgYKAQ4SARESFQHGX2Mi1qrmTzEh-YEYE7tkSZfU_RoVAUF8yKqnHCkVCaNCnmc9OM2jRhKX0076; LOGIN_INFO=AFmmF2swRgIhAOlPvQ5SsjllZSh--wdcqyXNhvMKhE4ni3K9Y4jPkR8VAiEAqEJWa1nB5f_F4G0D_lBSA1YTh9xJ7LuxXGBPs4xxiH8:QUQ3MjNmenFjYWNROUJVOW5WOVFWTFJpaU5JR2JoSTdZZUNtRHZVeTJCOEs4Q29aWGlOOVBfaDBIeHlYN1hNSDBDV0xBZy1uZTBXQ3g3MjZFY1ZOdXgzVnhqRHBVeGp0Y0tuLS1xaFJsSUxQRmIwYUNjRWFyWU90alkyZHI1TC0wWDJSUl85TE5YYWE0TzRNbS1IelNwNGUzc3RZSm5ZWmVn; __Secure-1PSIDTS=sidts-CjIB5H03P6M95wAm_cdSZhOxwU_t8F6ZvjFNKwq5_4yV1GXKwxL92mTMh6rWk9-NkbWRihAA; __Secure-3PSIDTS=sidts-CjIB5H03P6M95wAm_cdSZhOxwU_t8F6ZvjFNKwq5_4yV1GXKwxL92mTMh6rWk9-NkbWRihAA; __Secure-YEC=CgtzazEtUm9QM3RoNCjAp8zCBjIKCgJSVRIEGgAgPw%3D%3D; SIDCC=AKEyXzXLPn35i8IRC0gcCP48Ss0SU8tpIcnxoZ3sTNILC7yC_M7jqgsjeVdmy2ymkTfC_w78cc8; __Secure-1PSIDCC=AKEyXzUOnn7TabRgcWZtghPhKAdNtirT2uZ0hIk6zxtL0N5E2Zw2F-STNDhIhVk9ms3pLTxr040; __Secure-3PSIDCC=AKEyXzUPCd-jN1zWjr5ErrPdMYnvlOtishVOyHS1okxbviEsa-F_WngHr_fhgl9LU_TzrN-5Ezf2";

// Initialize Innertube once
let youtubeInstance = null;
async function initializeYoutube() {
  if (!youtubeInstance) {
    try {
      console.log('Initializing Innertube...');
      youtubeInstance = await Innertube.create({
        session: {
          cookie: cookieString
        }
      });
      console.log('Innertube initialized successfully.');
    } catch (error) {
      console.error('Failed to initialize Innertube:', error);
      throw error; // Re-throw to be caught by the route handler
    }
  }
  return youtubeInstance;
}

// API endpoint to get comments
app.get('/api/comments/:videoId', async (req, res) => {
  const { videoId } = req.params;

  if (!videoId) {
    return res.status(400).json({ error: 'Video ID is required' });
  }

  try {
    const youtube = await initializeYoutube();
    console.log(`Fetching comments for video ID: ${videoId}...`);
    const commentsResponse = await youtube.getComments(videoId);
    
    if (commentsResponse && commentsResponse.contents && commentsResponse.contents.length > 0) {
      const commentsData = commentsResponse.contents.map((commentThread, index) => {
        const authorName = commentThread.comment?.author?.name?.toString() || 'N/A';
        
        let commentText = 'N/A';
        if (commentThread.comment?.content?.item?.text) {
          commentText = commentThread.comment.content.item.text.toString();
        } else if (commentThread.comment?.content?.text) {
          commentText = commentThread.comment.content.text.toString();
        } else if (commentThread.comment?.content?.runs && commentThread.comment.content.runs.length > 0) {
          commentText = commentThread.comment.content.runs.map(run => run.text).join('');
        }
        
        return { author: authorName, text: commentText };
      });
      res.json(commentsData);
    } else {
      console.log('No comments found or response structure is unexpected.');
      res.status(404).json({ message: 'No comments found or response structure is unexpected.', response: commentsResponse });
    }

  } catch (error) {
    console.error('An error occurred while fetching comments:', error);
    res.status(500).json({ error: 'Failed to fetch comments', details: error.message });
  }
});

// Serve static files from the frontend directory
// This assumes your frontend is built and served from a 'frontend' directory
// Adjust the path if your frontend build output is elsewhere
app.use(express.static('frontend/build')); // Example: if your frontend is built into 'frontend/build'

// Fallback for frontend routing (if using a single-page application)
// This should be placed after your API routes
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'frontend', 'build', 'index.html'));
});


app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});