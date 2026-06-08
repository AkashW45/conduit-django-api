import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { ArticleService } from './article.service';
import { ArticleEntity } from './article.entity';
import { Comment } from './comment.entity';
import { UserEntity } from '../user/user.entity';
import { FollowsEntity } from '../profile/follows.entity';
import { getRepository } from 'typeorm';
import * as typeorm from 'typeorm';

jest.mock('typeorm', () => ({
  ...jest.requireActual('typeorm'),
  getRepository: jest.fn(),
}));

jest.mock('slug', () => jest.fn().mockReturnValue('test-slug'));

describe('ArticleService', () => {
  let service: ArticleService;
  let mockArticleRepo: any;
  let mockCommentRepo: any;
  let mockUserRepo: any;
  let mockFollowsRepo: any;
  let mockQueryBuilder: any;

  beforeEach(async () => {
    mockQueryBuilder = {
      leftJoinAndSelect: jest.fn().mockReturnThis(),
      where: jest.fn().mockReturnThis(),
      andWhere: jest.fn().mockReturnThis(),
      orderBy: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      offset: jest.fn().mockReturnThis(),
      getCount: jest.fn().mockResolvedValue(0),
      getMany: jest.fn().mockResolvedValue([]),
    };
    (getRepository as jest.Mock).mockReturnValue({
      createQueryBuilder: jest.fn().mockReturnValue(mockQueryBuilder),
    });

    mockArticleRepo = {
      findOne: jest.fn(),
      save: jest.fn(),
      delete: jest.fn(),
    };
    mockCommentRepo = {
      findOne: jest.fn(),
      save: jest.fn(),
      delete: jest.fn(),
    };
    mockUserRepo = {
      findOne: jest.fn(),
      save: jest.fn(),
    };
    mockFollowsRepo = {
      find: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ArticleService,
        { provide: getRepositoryToken(ArticleEntity), useValue: mockArticleRepo },
        { provide: getRepositoryToken(Comment), useValue: mockCommentRepo },
        { provide: getRepositoryToken(UserEntity), useValue: mockUserRepo },
        { provide: getRepositoryToken(FollowsEntity), useValue: mockFollowsRepo },
      ],
    }).compile();

    service = module.get<ArticleService>(ArticleService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('computeReadingTime', () => {
    it('should compute reading time correctly (edge cases, rounding, min 1)', () => {
      const helper = (service as any).computeReadingTime;

      // empty/null/white-space → min 1
      expect(helper('')).toBe(1);
      expect(helper(null)).toBe(1);
      expect(helper('   ')).toBe(1);

      // exactly 200 words → 1 minute
      const words200 = Array(200).fill('word').join(' ');
      expect(helper(words200)).toBe(1);

      // 201 words → 2 minutes (rounding up)
      const words201 = Array(201).fill('word').join(' ');
      expect(helper(words201)).toBe(2);

      // 500 words → 3 minutes (500/200 = 2.5 → ceil 3)
      const words500 = Array(500).fill('word').join(' ');
      expect(helper(words500)).toBe(3);
    });
  });

  describe('findAll', () => {
    it('should return articles with reading_time_minutes computed from body', async () => {
      // first article: short body (1 minute), second: 201 words (2 minutes), third: empty (1 minute)
      const longBody = Array(201).fill('word').join(' ');
      const mockArticles = [
        { id: 1, body: 'Simple body', slug: 'short' },
        { id: 2, body: longBody, slug: 'long' },
        { id: 3, body: '', slug: 'empty' },
      ];
      mockQueryBuilder.getMany.mockResolvedValue(mockArticles);
      mockQueryBuilder.getCount.mockResolvedValue(3);

      const result = await service.findAll({});
      expect(result.articles).toHaveLength(3);
      expect(result.articles[0].reading_time_minutes).toBe(1);
      expect(result.articles[1].reading_time_minutes).toBe(2);
      expect(result.articles[2].reading_time_minutes).toBe(1);
    });
  });

  describe('findOne', () => {
    it('should add reading_time_minutes when found, and return {article:null} when not found', async () => {
      // found case
      const mockArticle = { id: 1, body: 'a few words', slug: 'test' };
      mockArticleRepo.findOne.mockResolvedValue(mockArticle);
      const found = await service.findOne({ slug: 'test' });
      expect(found.article.reading_time_minutes).toBe(1);

      // not found
      mockArticleRepo.findOne.mockResolvedValue(undefined);
      const notFound = await service.findOne({ slug: 'nonexistent' });
      expect(notFound.article).toBeUndefined();
    });
  });

  describe('create', () => {
    it('should set reading_time_minutes on the newly created article', async () => {
      const dto = { title: 'New', description: 'Desc', body: 'Ten simple words in the article body', tagList: [] };
      mockArticleRepo.save.mockResolvedValue({ id: 1, slug: 'test-slug', body: dto.body });
      mockUserRepo.findOne.mockResolvedValue({ id: 1, articles: [] });

      const result = await service.create(1, dto);
      expect(result.reading_time_minutes).toBe(1); // 10 words → ceil(10/200)=1
    });
  });

  describe('update', () => {
    it('should set reading_time_minutes on the updated article', async () => {
      const oldArticle = { id: 1, slug: 'test', body: 'Old short body' };
      const updatedData = { body: 'Updated body with some more words but still under 200' };
      mockArticleRepo.findOne.mockResolvedValue(oldArticle);
      mockArticleRepo.save.mockResolvedValue({ ...oldArticle, ...updatedData });

      const result = await service.update('test', updatedData);
      // body: 'Updated body with some more words but still under 200' → 10 words → 1
      expect(result.article.reading_time_minutes).toBe(1);
    });
  });
});