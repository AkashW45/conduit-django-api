package io.spring.application;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

import io.spring.application.data.ArticleData;
import io.spring.application.data.ArticleDataList;
import io.spring.application.data.ArticleFavoriteCount;
import io.spring.application.data.ProfileData;
import io.spring.core.user.User;
import io.spring.infrastructure.mybatis.readservice.ArticleFavoritesReadService;
import io.spring.infrastructure.mybatis.readservice.ArticleReadService;
import io.spring.infrastructure.mybatis.readservice.UserRelationshipQueryService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

@ExtendWith(MockitoExtension.class)
class ArticleQueryServiceTests {

    @Mock
    private ArticleReadService articleReadService;

    @Mock
    private UserRelationshipQueryService userRelationshipQueryService;

    @Mock
    private ArticleFavoritesReadService articleFavoritesReadService;

    @Mock
    private User user;

    @InjectMocks
    private ArticleQueryService articleQueryService;

    private ArticleData articleSpy;

    @BeforeEach
    void setUp() {
        articleSpy = spy(new ArticleData());
        ProfileData profileData = mock(ProfileData.class);
        when(profileData.getId()).thenReturn("profileId");
        articleSpy.setProfileData(profileData);
        // simulate user-favorite calls for single article fillExtraInfo
        when(articleFavoritesReadService.isUserFavorite(anyString(), anyString())).thenReturn(false);
        when(articleFavoritesReadService.articleFavoriteCount(anyString())).thenReturn(0);
        when(userRelationshipQueryService.isUserFollowing(anyString(), anyString())).thenReturn(false);
    }

    @Test
    void shouldComputeReadingTimeFor300WordsBody() {
        String body = generateWords(300);
        when(articleSpy.getBody()).thenReturn(body);
        when(articleReadService.findBySlug(anyString())).thenReturn(articleSpy);

        Optional<ArticleData> result = articleQueryService.findBySlug("test-slug", user);

        assertEquals(true, result.isPresent());
        verify(articleSpy).setReadingTimeMinutes(2);
    }

    @Test
    void shouldComputeReadingTimeFor200WordsBody() {
        String body = generateWords(200);
        when(articleSpy.getBody()).thenReturn(body);
        when(articleReadService.findBySlug(anyString())).thenReturn(articleSpy);

        articleQueryService.findBySlug("test-slug", user);

        verify(articleSpy).setReadingTimeMinutes(1);
    }

    @Test
    void shouldReturnMinimumReadingTimeOfOneForNullBody() {
        when(articleSpy.getBody()).thenReturn(null);
        when(articleReadService.findById(anyString())).thenReturn(articleSpy);

        Optional<ArticleData> result = articleQueryService.findById("1", user);

        assertTrue(result.isPresent());
        verify(articleSpy).setReadingTimeMinutes(1);
    }

    @Test
    void shouldReturnMinimumReadingTimeOfOneForEmptyBody() {
        when(articleSpy.getBody()).thenReturn("");
        when(articleReadService.findById(anyString())).thenReturn(articleSpy);

        Optional<ArticleData> result = articleQueryService.findById("1", user);

        assertTrue(result.isPresent());
        verify(articleSpy).setReadingTimeMinutes(1);
    }

    @Test
    void shouldSetReadingTimeForAllArticlesInListEvenWhenUserIsNull() {
        ArticleData article1 = spy(new ArticleData());
        ArticleData article2 = spy(new ArticleData());
        ProfileData profile = mock(ProfileData.class);
        when(profile.getId()).thenReturn("id");
        article1.setProfileData(profile);
        article2.setProfileData(profile);
        when(article1.getBody()).thenReturn("hello world");      // 2 words -> 1 min
        when(article2.getBody()).thenReturn(generateWords(250)); // 250 words -> 2 mins

        List<String> ids = Arrays.asList("1", "2");
        when(articleReadService.queryArticles(null, null, null, null)).thenReturn(ids);
        when(articleReadService.countArticle(null, null, null)).thenReturn(2);
        List<ArticleData> articles = Arrays.asList(article1, article2);
        when(articleReadService.findArticles(ids)).thenReturn(articles);

        ArticleDataList result = articleQueryService.findRecentArticles(null, null, null, null, null);

        assertEquals(2, result.getCount());
        verify(article1).setReadingTimeMinutes(1);
        verify(article2).setReadingTimeMinutes(2);
    }

    private String generateWords(int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append("word ");
        }
        return sb.toString().trim();
    }
}