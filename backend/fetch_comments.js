const { Innertube } = require('youtubei.js');
const fs = require('fs');

// Cookie string extracted from the user's provided JSON
const cookieString = "PREF=f4=4000000&f6=40000000&tz=Europe.Moscow&f7=100&f5=20000; HSID=AzIts3EOJ8M_Q72rd; SSID=AwS26jNssxnqWMjv2; APISID=lKbFNr8-gEjQigyh/AbryCn3EZKmvFUYgd; SAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; __Secure-1PAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; __Secure-3PAPISID=9mi3cM12kTWg6slr/AKBFC_dZ826tzLdM-; SID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlNUX5ab5WrJ8clM_lHg9KQ3wACgYKAXASARESFQHGX2Mi8zhJ89vsBxFLJiBRXf6xNBoVAUF8yKqVOoyjzKAqBZO_r-dHlNfv0076; __Secure-1PSID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlN8bKdDZ0HsyGZvNugHa6SjAACgYKAaMSARESFQHGX2Midsz_tu_lI2VHVU1-_Mdo8hoVAUF8yKqY-ZFNI6xB8HDbJQNaakgU0076; __Secure-3PSID=g.a000yAjjEBFeY-cVr3LM7N8CsNqcKuj-yvQAbNM4gilGCfB4RtlNSeaU4OJpzEaEkEHsUgnUDAACgYKAQ4SARESFQHGX2Mi1qrmTzEh-YEYE7tkSZfU_RoVAUF8yKqnHCkVCaNCnmc9OM2jRhKX0076; LOGIN_INFO=AFmmF2swRgIhAOlPvQ5SsjllZSh--wdcqyXNhvMKhE4ni3K9Y4jPkR8VAiEAqEJWa1nB5f_F4G0D_lBSA1YTh9xJ7LuxXGBPs4xxiH8:QUQ3MjNmenFjYWNROUJVOW5WOVFWTFJpaU5JR2JoSTdZZUNtRHZVeTJCOEs4Q29aWGlOOVBfaDBIeHlYN1hNSDBDV0xBZy1uZTBXQ3g3MjZFY1ZOdXgzVnhqRHBVeGp0Y0tuLS1xaFJsSUxQRmIwYUNjRWFyWU90alkyZHI1TC0wWDJSUl85TE5YYWE0TzRNbS1IelNwNGUzc3RZSm5ZWmVn; __Secure-1PSIDTS=sidts-CjIB5H03P6M95wAm_cdSZhOxwU_t8F6ZvjFNKwq5_4yV1GXKwxL92mTMh6rWk9-NkbWRihAA; __Secure-3PSIDTS=sidts-CjIB5H03P6M95wAm_cdSZhOxwU_t8F6ZvjFNKwq5_4yV1GXKwxL92mTMh6rWk9-NkbWRihAA; __Secure-YEC=CgtzazEtUm9QM3RoNCjAp8zCBjIKCgJSVRIEGgAgPw%3D%3D; SIDCC=AKEyXzXLPn35i8IRC0gcCP48Ss0SU8tpIcnxoZ3sTNILC7yC_M7jqgsjeVdmy2ymkTfC_w78cc8; __Secure-1PSIDCC=AKEyXzUOnn7TabRgcWZtghPhKAdNtirT2uZ0hIk6zxtL0N5E2Zw2F-STNDhIhVk9ms3pLTxr040; __Secure-3PSIDCC=AKEyXzUPCd-jN1zWjr5ErrPdMYnvlOtishVOyHS1okxbviEsa-F_WngHr_fhgl9LU_TzrN-5Ezf2";

const videoId = 'Vsu6PawXJGk';

(async () => {
  try {
    console.log('Initializing Innertube with cookies...');
    const youtube = await Innertube.create({
      session: {
        cookie: cookieString
      }
    });
    console.log('Innertube initialized successfully.');

    console.log(`Fetching comments for video ID: ${videoId}...`);
    const commentsResponse = await youtube.getComments(videoId);
    
    if (commentsResponse && commentsResponse.contents && commentsResponse.contents.length > 0) {
      console.log(`Found ${commentsResponse.contents.length} comments. Displaying the first 5:`);
      commentsResponse.contents.slice(0, 5).forEach((commentThread, index) => {
        // Accessing author and content from CommentThread -> comment -> author/content
        const authorName = commentThread.comment?.author?.name?.toString() || 'N/A';
        
        // Attempting to access comment text more robustly
        let commentText = 'N/A';
        if (commentThread.comment?.content?.item?.text) {
          commentText = commentThread.comment.content.item.text.toString();
        } else if (commentThread.comment?.content?.text) { // Fallback if structure is simpler
          commentText = commentThread.comment.content.text.toString();
        } else if (commentThread.comment?.content?.runs && commentThread.comment.content.runs.length > 0) { // If content is an array of runs
          commentText = commentThread.comment.content.runs.map(run => run.text).join('');
        }
        
        console.log(`${index + 1}. Author: ${authorName}, Text: ${commentText}`);
      });
    } else {
      console.log('No comments found or response structure is unexpected.');
      console.log('Full response:', commentsResponse);
    }

  } catch (error) {
    console.error('An error occurred:', error);
  }
})();