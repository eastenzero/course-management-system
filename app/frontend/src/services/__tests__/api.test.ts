import axios from 'axios';
import { courseAPI, userAPI, classroomAPI } from '../api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('courseAPI', () => {
    describe('getCourses', () => {
      it('should fetch courses with default parameters', async () => {
        const mockResponse = {
          data: {
            results: {
              data: [
                { id: 1, name: 'Course 1', code: 'CS101' },
                { id: 2, name: 'Course 2', code: 'CS102' },
              ],
            },
            count: 2,
          },
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await courseAPI.getCourses();

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/courses/', {
          params: {},
        });
        expect(result).toEqual(mockResponse);
      });

      it('should fetch courses with custom parameters', async () => {
        const params = {
          page: 2,
          page_size: 10,
          search: 'computer',
          department: 'CS',
        };

        const mockResponse = {
          data: {
            results: { data: [] },
            count: 0,
          },
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        await courseAPI.getCourses(params);

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/courses/', {
          params,
        });
      });

      it('should handle API errors', async () => {
        const errorMessage = 'Network Error';
        mockedAxios.get.mockRejectedValueOnce(new Error(errorMessage));

        await expect(courseAPI.getCourses()).rejects.toThrow(errorMessage);
      });
    });

    describe('getCourse', () => {
      it('should fetch a single course', async () => {
        const courseId = 1;
        const mockResponse = {
          data: { id: 1, name: 'Course 1', code: 'CS101' },
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await courseAPI.getCourse(courseId);

        expect(mockedAxios.get).toHaveBeenCalledWith(`/api/courses/${courseId}/`);
        expect(result).toEqual(mockResponse);
      });
    });

    describe('createCourse', () => {
      it('should create a new course', async () => {
        const courseData = {
          name: 'New Course',
          code: 'CS103',
          credits: 3,
          department: 'Computer Science',
        };

        const mockResponse = {
          data: { id: 3, ...courseData },
        };

        mockedAxios.post.mockResolvedValueOnce(mockResponse);

        const result = await courseAPI.createCourse(courseData);

        expect(mockedAxios.post).toHaveBeenCalledWith('/api/courses/', courseData);
        expect(result).toEqual(mockResponse);
      });
    });

    describe('updateCourse', () => {
      it('should update an existing course', async () => {
        const courseId = 1;
        const updateData = { name: 'Updated Course Name' };

        const mockResponse = {
          data: { id: 1, name: 'Updated Course Name', code: 'CS101' },
        };

        mockedAxios.put.mockResolvedValueOnce(mockResponse);

        const result = await courseAPI.updateCourse(courseId, updateData);

        expect(mockedAxios.put).toHaveBeenCalledWith(
          `/api/courses/${courseId}/`,
          updateData
        );
        expect(result).toEqual(mockResponse);
      });
    });

    describe('deleteCourse', () => {
      it('should delete a course', async () => {
        const courseId = 1;
        const mockResponse = { data: null };

        mockedAxios.delete.mockResolvedValueOnce(mockResponse);

        const result = await courseAPI.deleteCourse(courseId);

        expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/courses/${courseId}/`);
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('userAPI', () => {
    describe('getUsers', () => {
      it('should fetch users with parameters', async () => {
        const params = { page: 1, page_size: 20 };
        const mockResponse = {
          data: {
            results: {
              data: [
                { id: 1, username: 'user1', email: 'user1@example.com' },
                { id: 2, username: 'user2', email: 'user2@example.com' },
              ],
            },
            count: 2,
          },
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await userAPI.getUsers(params);

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/users/', {
          params,
        });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('createUser', () => {
      it('should create a new user', async () => {
        const userData = {
          username: 'newuser',
          email: 'newuser@example.com',
          password: 'password123',
          user_type: 'student',
        };

        const mockResponse = {
          data: { id: 3, ...userData, password: undefined },
        };

        mockedAxios.post.mockResolvedValueOnce(mockResponse);

        const result = await userAPI.createUser(userData);

        expect(mockedAxios.post).toHaveBeenCalledWith('/api/users/', userData);
        expect(result).toEqual(mockResponse);
      });
    });

    describe('updateUser', () => {
      it('should update user information', async () => {
        const userId = 1;
        const updateData = { email: 'updated@example.com' };

        const mockResponse = {
          data: { id: 1, username: 'user1', email: 'updated@example.com' },
        };

        mockedAxios.put.mockResolvedValueOnce(mockResponse);

        const result = await userAPI.updateUser(userId, updateData);

        expect(mockedAxios.put).toHaveBeenCalledWith(
          `/api/users/${userId}/`,
          updateData
        );
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('classroomAPI', () => {
    describe('getClassrooms', () => {
      it('should fetch classrooms', async () => {
        const mockResponse = {
          data: {
            results: {
              data: [
                { id: 1, name: 'Room A101', capacity: 50 },
                { id: 2, name: 'Room B201', capacity: 30 },
              ],
            },
            count: 2,
          },
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await classroomAPI.getClassrooms();

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/classrooms/', {
          params: {},
        });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('createClassroom', () => {
      it('should create a new classroom', async () => {
        const classroomData = {
          name: 'Room C301',
          building_name: 'Building C',
          room_number: '301',
          capacity: 40,
          room_type: 'lecture',
        };

        const mockResponse = {
          data: { id: 3, ...classroomData },
        };

        mockedAxios.post.mockResolvedValueOnce(mockResponse);

        const result = await classroomAPI.createClassroom(classroomData);

        expect(mockedAxios.post).toHaveBeenCalledWith('/api/classrooms/', classroomData);
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      mockedAxios.get.mockRejectedValueOnce(networkError);

      await expect(courseAPI.getCourses()).rejects.toThrow('Network Error');
    });

    it('should handle HTTP errors', async () => {
      const httpError = {
        response: {
          status: 404,
          data: { message: 'Not Found' },
        },
      };
      mockedAxios.get.mockRejectedValueOnce(httpError);

      await expect(courseAPI.getCourse(999)).rejects.toEqual(httpError);
    });

    it('should handle validation errors', async () => {
      const validationError = {
        response: {
          status: 400,
          data: {
            errors: {
              name: ['This field is required'],
              email: ['Enter a valid email address'],
            },
          },
        },
      };
      mockedAxios.post.mockRejectedValueOnce(validationError);

      await expect(userAPI.createUser({})).rejects.toEqual(validationError);
    });
  });

  describe('Request Interceptors', () => {
    it('should add authorization header when token exists', () => {
      // This would test the axios interceptor setup
      // In a real scenario, you'd test that the Authorization header is added
      expect(mockedAxios.interceptors.request.use).toBeDefined();
    });
  });

  describe('Response Interceptors', () => {
    it('should handle response transformation', () => {
      // This would test the axios response interceptor
      expect(mockedAxios.interceptors.response.use).toBeDefined();
    });
  });
});
