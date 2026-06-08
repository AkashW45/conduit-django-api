import { ArticleController } from './article.controller';
import { ArticleService } from './article.service';
import { ArticlesRO, ArticleRO } from './article.interface';

describe('ArticleController', () => {
  let controller: ArticleController;
  let mockArticleService: jest.Mocked<Partial<ArticleService>>;

  const mockArticle = {
    slug: 'test-slug',
    title: 'Test Article',
    body: 'hello world',
    description: 'Test',
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockArticleRO: ArticleRO = { article: mockArticle };
  const mockArticlesRO: ArticlesRO = { articles: [mockArticle], articlesCount: 1 };

  beforeEach(() => {
    mockArticleService = {
      findAll: jest.fn().mockResolvedValue(mockArticlesRO),
      findFeed: jest.fn().mockResolvedValue(mockArticlesRO),
      findOne: jest.fn().mockResolvedValue(mockArticleRO),
      create: jest.fn().mockResolvedValue(mockArticleRO),
      update: jest.fn().mockResolvedValue(mockArticleRO),
      favorite: jest.fn().mockResolvedValue(mockArticleRO),
      unFavorite: jest.fn().mockResolvedValue(mockArticleRO),
      findComments: jest.fn(),
      addComment: jest.fn(),
      deleteComment: jest.fn(),
    } as unknown as jest.Mocked<ArticleService>;

    controller = new ArticleController(mockArticleService as ArticleService);
  });

  it('should compute reading_time_minutes for articles in findAll', async () => {
    const result = await controller.findAll({});
    expect(result.articles[0]).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for articles in getFeed', async () => {
    const result = await controller.getFeed(1, {});
    expect(result.articles[0]).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for findOne', async () => {
    const result = await controller.findOne('test');
    expect(result.article).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for create', async () => {
    const result = await controller.create(1, { body: 'hello world' });
    expect(result.article).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for update', async () => {
    const result = await controller.update({ slug: 'test' }, { body: 'hello world' });
    expect(result.article).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for favorite', async () => {
    const result = await controller.favorite(1, 'test');
    expect(result.article).toHaveProperty('reading_time_minutes', 1);
  });

  it('should compute reading_time_minutes for unFavorite', async () => {
    const result = await controller.unFavorite(1, 'test');
    expect(result.article).toHaveProperty('reading_time_minutes', 1);
  });

  it('should return minimum 1 minute for empty body', async () => {
    const articleWithoutBody = { ...mockArticle, body: '' };
    const articleRO = { article: articleWithoutBody };
    mockArticleService.findOne = jest.fn().mockResolvedValue(articleRO);
    const result = await controller.findOne('test');
    expect(result.article.reading_time_minutes).toBe(1);
  });

  it('should return minimum 1 minute for undefined body', async () => {
    const articleWithoutBody = { ...mockArticle, body: undefined };
    const articleRO = { article: articleWithoutBody };
    mockArticleService.findOne = jest.fn().mockResolvedValue(articleRO);
    const result = await controller.findOne('test');
    expect(result.article.reading_time_minutes).toBe(1);
  });

  it('should round up reading time for many words', async () => {
    const manyWords = Array(250).fill('word').join(' '); // 250 words
    const articleLong = { ...mockArticle, body: manyWords };
    const articleROLong = { article: articleLong };
    mockArticleService.findOne = jest.fn().mockResolvedValue(articleROLong);
    const result = await controller.findOne('test');
    expect(result.article.reading_time_minutes).toBe(2); // ceil(250/200) = 2
  });
});