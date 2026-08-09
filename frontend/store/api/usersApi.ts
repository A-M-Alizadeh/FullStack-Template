import type { User, UserRole } from "@/types/auth";

import { baseApi } from "./baseApi";

export type UserCreateBody = {
  email: string;
  password: string;
  role: UserRole;
};

export type UserUpdateBody = {
  email?: string;
  password?: string;
  role?: UserRole;
};

export const usersApi = baseApi.injectEndpoints({
  overrideExisting: process.env.NODE_ENV === "development",
  endpoints: (build) => ({
    listUsers: build.query<User[], void>({
      query: () => "/users",
      providesTags: ["Users"],
    }),
    createUser: build.mutation<User, UserCreateBody>({
      query: (body) => ({
        url: "/users",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Users"],
    }),
    updateUser: build.mutation<User, { id: string; body: UserUpdateBody }>({
      query: ({ id, body }) => ({
        url: `/users/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Users"],
    }),
    deleteUser: build.mutation<void, string>({
      query: (id) => ({
        url: `/users/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Users"],
    }),
  }),
});

export const {
  useListUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = usersApi;
