package io.spring.graphql;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import io.spring.application.data.ArticleData;
import io.spring.graphql.types.Article;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ArticleDatafetcherTests {

    @Mock
    private io.spring.application.ArticleQueryService articleQueryService;

    @Mock
    private io.spring.core.user.UserRepository userRepository;

    private ArticleDatafetcher articleDatafetcher;
    private Method computeReadingTimeMinutesMethod;
    private Method buildArticleResultMethod;

    @BeforeEach
    void setUp() throws Exception {
        articleDatafetcher = new ArticleDatafetcher(articleQueryService, userRepository);
        computeReadingTimeMinutesMethod = ArticleDatafetcher.class.getDeclaredMethod(
                "computeReadingTimeMinutes", String.class);
        computeReadingTimeMinutesMethod.setAccessible(true);
        buildArticleResultMethod = ArticleDatafetcher.class.getDeclaredMethod(
                "buildArticleResult", ArticleData.class);
        buildArticleResultMethod.setAccessible(true);
    }

    private int invokeComputeReadingTimeMinutes(String body) throws Exception {
        try {
            return (int) computeReadingTimeMinutesMethod.invoke(articleDatafetcher, body);
        } catch (InvocationTargetException e) {
            throw (Exception) e.getCause();
        }
    }

    private Article invokeBuildArticleResult(ArticleData articleData) throws Exception {
        try {
            return (Article) buildArticleResultMethod.invoke(articleDatafetcher, articleData);
        } catch (InvocationTargetException e) {
            throw (Exception) e.getCause();
        }
    }

    @Test
    @DisplayName("null body returns 1")
    void testComputeReadingTimeMinutes_nullBody_returnsOne() throws Exception {
        int result = invokeComputeReadingTimeMinutes(null);
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("empty body returns 1")
    void testComputeReadingTimeMinutes_emptyBody_returnsOne() throws Exception {
        int result = invokeComputeReadingTimeMinutes("");
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("body with only whitespace returns 1")
    void testComputeReadingTimeMinutes_onlyWhitespace_returnsOne() throws Exception {
        int result = invokeComputeReadingTimeMinutes("   \t\n  ");
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("body with mixed whitespace separates words correctly")
    void testComputeReadingTimeMinutes_mixedWhitespace() throws Exception {
        String body = "word1  word2\tword3\nword4";
        int result = invokeComputeReadingTimeMinutes(body);
        // 4 words, ceil(4/200) = 1
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("199 words returns 1")
    void testComputeReadingTimeMinutes_199words_returnsOne() throws Exception {
        String body = generateWords(199);
        int result = invokeComputeReadingTimeMinutes(body);
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("200 words returns 1")
    void testComputeReadingTimeMinutes_200words_returnsOne() throws Exception {
        String body = generateWords(200);
        int result = invokeComputeReadingTimeMinutes(body);
        assertThat(result).isEqualTo(1);
    }

    @Test
    @DisplayName("201 words returns 2")
    void testComputeReadingTimeMinutes_201words_returnsTwo() throws Exception {
        String body = generateWords(201);
        int result = invokeComputeReadingTimeMinutes(body);
        assertThat(result).isEqualTo(2);
    }

    @Test
    @DisplayName("400 words returns 2")
    void testComputeReadingTimeMinutes_400words_returnsTwo() throws Exception {
        String body = generateWords(400);
        int result = invokeComputeReadingTimeMinutes(body);
        assertThat(result).isEqualTo(2);
    }

    @Test
    @DisplayName("buildArticleResult sets readingTimeMinutes based on body")
    void testBuildArticleResult_includesReadingTimeMinutes() throws Exception {
        String body = "This is a test article with exactly nine words here.";
        ArticleData articleData = mockArticleData(body, "test-slug", "Test Title");

        Article result = invokeBuildArticleResult(articleData);

        assertThat(result.getReadingTimeMinutes()).isEqualTo(1); // 9/200 ceil = 1
        assertThat(result.getSlug()).isEqualTo("test-slug");
        assertThat(result.getTitle()).isEqualTo("Test Title");
    }

    private String generateWords(int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            if (i > 0) sb.append(" ");
            sb.append("word");
        }
        return sb.toString();
    }

    private ArticleData mockArticleData(String body, String slug, String title) {
        ArticleData articleData = org.mockito.Mockito.mock(ArticleData.class);
        when(articleData.getBody()).thenReturn(body);
        when(articleData.getSlug()).thenReturn(slug);
        when(articleData.getTitle()).thenReturn(title);
        when(articleData.getDescription()).thenReturn("desc");
        when(articleData.getTagList()).thenReturn(java.util.Collections.emptyList());
        when(articleData.getCreatedAt()).thenReturn(org.joda.time.DateTime.now());
        when(articleData.getUpdatedAt()).thenReturn(org.joda.time.DateTime.now());
        when(articleData.isFavorited()).thenReturn(false);
        when(articleData.getFavoritesCount()).thenReturn(0);
        return articleData;
    }
}