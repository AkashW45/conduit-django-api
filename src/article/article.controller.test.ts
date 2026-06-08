import { ArticleController } from './article.controller';
import { ArticleService } from './article.service';
import { CreateArticleDto } from './dto';

describe('ArticleController', () => {
  let controller: ArticleController;
  let mockArticleService: jest.Mocked<Partial<ArticleService>>;

  beforeEach(() => {
    mockArticleService = {
      findAll: jest.fn(),
      findFeed: jest.fn(),
      findOne: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      addComment: jest.fn(),
      deleteComment: jest.fn(),
      favorite: jest.fn(),
      unFavorite: jest.fn(),
      findComments: jest.fn(),
    };
    controller = new ArticleController(mockArticleService as ArticleService);
  });

  describe('addReadingTime integration', () => {
    it('should add reading_time_minutes to every article in an array response', async () => {
      const articles = [
        { slug: 'a', body: 'word1 word2 word3', title: 'A' },
        { slug: 'b', body: Array(200).fill('word').join(' '), title: 'B' },
        { slug: 'c', body: Array(201).fill('word').join(' '), title: 'C' },
        { slug: 'd', body: '', title: 'D' },
        { slug: 'e', body: undefined, title: 'E' },
      ];
      mockArticleService.findAll.mockResolvedValue({
        articles,
        articlesCount: articles.length,
      });

      const result = await controller.findAll({});

      expect(result.articles[0].reading_time_minutes).toBe(1);
      expect(result.articles[1].reading_time_minutes).toBe(1); // 200/200=1
      expect(result.articles[2].reading_time_minutes).toBe(2); // 201/200=1.005 -> ceil=2
      expect(result.articles[3].reading_time_minutes).toBe(1); // empty
      expect(result.articles[4].reading_time_minutes).toBe(1); // undefined
    });

    it('should add reading_time_minutes to a single article response', async () => {
      const article = { slug: 'test', body: 'one two three four five', title: 'test' };
      mockArticleService.findOne.mockResolvedValue({ article });

      const result = await controller.findOne('test');

      expect(result.article.reading_time_minutes).toBe(1);
    });

    it('should set reading_time_minutes to 1 when article body is empty', async () => {
      const article = { slug: 'empty', body: '', title: 'empty' };
      mockArticleService.findOne.mockResolvedValue({ article });

      const result = await controller.findOne('empty');

      expect(result.article.reading_time_minutes).toBe(1);
    });

    it('should round up reading_time_minutes correctly for word counts not divisible by 200', async () => {
      const article = { slug: 'round', body: Array(201).fill('word').join(' ') };
      mockArticleService.findOne.mockResolvedValue({ article });

      const result = await controller.findOne('round');

      expect(result.article.reading_time_minutes).toBe(2);
    });

    it('should add reading_time_minutes to the article returned from create', async () => {
      const articleData: CreateArticleDto = {
        title: 'new',
        description: 'desc',
        body: 'a b c',
      };
      const createdArticle = { slug: 'new', body: 'a b c', title: 'new' };
      mockArticleService.create.mockResolvedValue({ article: createdArticle });

      const result = await controller.create(1, articleData);

      expect(result.article.reading_time_minutes).toBe(1);
    });

    it('should add reading_time_minutes to the article returned from favorite', async () => {
      const article = { slug: 'fav', body: 'word word word word word', title: 'fav' };
      mockArticleService.favorite.mockResolvedValue({ article });

      const result = await controller.favorite(1, 'fav');

      expect(result.article.reading_time_minutes).toBe(1);
    });
  });
});