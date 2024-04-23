import { IFile, IFolder } from '@/interfaces/database/file-manager';
import fileManagerService from '@/services/fileManagerService';
import { DvaModel } from 'umi';

export interface FileManagerModelState {
  fileList: IFile[];
  parentFolderList: IFolder[];
}

const model: DvaModel<FileManagerModelState> = {
  namespace: 'fileManager',
  state: { fileList: [], parentFolderList: [] },
  reducers: {
    setFileList(state, { payload }) {
      return { ...state, fileList: payload };
    },
    setParentFolderList(state, { payload }) {
      return { ...state, parentFolderList: payload };
    },
  },
  effects: {
    *removeFile({ payload = {} }, { call, put }) {
      const { data } = yield call(fileManagerService.removeFile, payload);
      const { retcode } = data;
      if (retcode === 0) {
        yield put({
          type: 'listFile',
          payload: data.data?.files ?? [],
        });
      }
    },
    *listFile({ payload = {} }, { call, put }) {
      const { data } = yield call(fileManagerService.listFile, payload);
      const { retcode, data: res } = data;

      if (retcode === 0 && Array.isArray(res.files)) {
        yield put({
          type: 'setFileList',
          payload: res.files,
        });
      }
    },
    *renameFile({ payload = {} }, { call, put }) {
      const { data } = yield call(fileManagerService.renameFile, payload);
      if (data.retcode === 0) {
        yield put({ type: 'listFile' });
      }
      return data.retcode;
    },
    *getAllParentFolder({ payload = {} }, { call, put }) {
      const { data } = yield call(
        fileManagerService.getAllParentFolder,
        payload,
      );
      if (data.retcode === 0) {
        yield put({
          type: 'setParentFolderList',
          payload: data.data?.parent_folders ?? [],
        });
      }
      return data.retcode;
    },
  },
};
export default model;
