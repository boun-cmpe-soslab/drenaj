package direnaj.functionalities.nlp;

import java.util.ArrayList;
import java.util.List;

import direnaj.functionalities.nlp.WordStringUtils;
import direnaj.functionalities.nlp.TweetParseUtil;

public class ConceptElicitor {
	
	static ArrayList<String> getCleanWords(String rawTweet) {
		String cleanTweet = WordStringUtils.removeStopwords(rawTweet);
		
		cleanTweet = TweetParseUtil.onlyText(cleanTweet);
		
		ArrayList<String> words = new ArrayList<String>();
		
		for(String word : cleanTweet.split(" ")) {
			if (word.length() > 1) {
				word = word.replaceAll(":", "");
				words.add(word);
			}
		}
		
		return words;
	}
	
	
	static ArrayList<String> tweetRelatedConcepts(String tweet) {
		
		List<String> tags = TweetParseUtil.getHashtagsInText(tweet);
		
		ArrayList<String> words = getCleanWords(tweet);
		
		/*
		for (String word : words) {
			System.out.println(word);
		}
		*/
		
		Synset s = new Synset
		
		
		
		return new ArrayList();
	}
	
	public static void main(String[] args) {
		ConceptElicitor.tweetRelatedConcepts("Who was Albert Wohlstetter? What was \"Team B\"? Who wants to lead the U.S. into Syria? You should know: 'In the... http://t.co/QkF6Ojozjx");
	}
}
