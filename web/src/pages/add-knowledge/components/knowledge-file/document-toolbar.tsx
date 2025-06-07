import { ReactComponent as CancelIcon } from '@/assets/svg/cancel.svg';
import { ReactComponent as DeleteIcon } from '@/assets/svg/delete.svg';
import { ReactComponent as DisableIcon } from '@/assets/svg/disable.svg';
import { ReactComponent as EnableIcon } from '@/assets/svg/enable.svg';
import { ReactComponent as RunIcon } from '@/assets/svg/run.svg';
import { useShowDeleteConfirm, useTranslate } from '@/hooks/common-hooks';
import {
  useRemoveNextDocument,
  useRunNextDocument,
  useSetNextDocumentStatus,
} from '@/hooks/document-hooks';
import { IDocumentInfo } from '@/interfaces/database/document';
import {
  DownOutlined,
  FileOutlined,
  FileTextOutlined,
  PlusOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Button, Dropdown, Flex, Input, MenuProps, Space } from 'antd';
import { useCallback, useMemo } from 'react';
import { toast } from 'sonner';
import { RunningStatus } from './constant';
import {
  SortAscendingOutlined,
  SortDescendingOutlined,
  SwapOutlined,
} from '@ant-design/icons';

import styles from './index.less';

interface IProps {
  selectedRowKeys: string[];
  showCreateModal(): void;
  showWebCrawlModal(): void;
  showDocumentUploadModal(): void;
  searchString: string;
  handleInputChange: React.ChangeEventHandler<HTMLInputElement>;
  documents: IDocumentInfo[];
  sortOrder?: 'asc' | 'desc' | '';
  toggleSortOrder?: () => void;
}

const DocumentToolbar = ({
  searchString,
  selectedRowKeys,
  showCreateModal,
  showDocumentUploadModal,
  handleInputChange,
  documents,
  sortOrder = '',
  toggleSortOrder = () => {},
}: IProps) => {
  const { t } = useTranslate('knowledgeDetails');
  const { removeDocument } = useRemoveNextDocument();
  const showDeleteConfirm = useShowDeleteConfirm();
  const { runDocumentByIds } = useRunNextDocument();
  const { setDocumentStatus } = useSetNextDocumentStatus();

  const actionItems: MenuProps['items'] = useMemo(() => {
    return [
      {
        key: '1',
        onClick: showDocumentUploadModal,
        label: (
          <div>
            <Button type="link">
              <Space>
                <FileTextOutlined />
                {t('localFiles')}
              </Space>
            </Button>
          </div>
        ),
      },
      { type: 'divider' },
      {
        key: '3',
        onClick: showCreateModal,
        label: (
          <div>
            <Button type="link">
              <FileOutlined />
              {t('emptyFiles')}
            </Button>
          </div>
        ),
      },
    ];
  }, [showDocumentUploadModal, showCreateModal, t]);

  const handleDelete = useCallback(() => {
    const deletedKeys = selectedRowKeys.filter(
      (x) =>
        !documents
          .filter((y) => y.run === RunningStatus.RUNNING)
          .some((y) => y.id === x),
    );
    if (deletedKeys.length === 0) {
      toast.error(t('theDocumentBeingParsedCannotBeDeleted'));
      return;
    }
    showDeleteConfirm({
      onOk: () => {
        removeDocument(deletedKeys);
      },
    });
  }, [selectedRowKeys, showDeleteConfirm, documents, t, removeDocument]);

  const runDocument = useCallback(
    (run: number) => {
      runDocumentByIds({
        documentIds: selectedRowKeys,
        run,
        shouldDelete: false,
      });
    },
    [runDocumentByIds, selectedRowKeys],
  );

  const handleRunClick = useCallback(() => {
    runDocument(1);
  }, [runDocument]);

  const handleCancelClick = useCallback(() => {
    runDocument(2);
  }, [runDocument]);

  const onChangeStatus = useCallback(
    (enabled: boolean) => {
      selectedRowKeys.forEach((id) => {
        setDocumentStatus({ status: enabled, documentId: id });
      });
    },
    [selectedRowKeys, setDocumentStatus],
  );

  const handleEnableClick = useCallback(() => {
    onChangeStatus(true);
  }, [onChangeStatus]);

  const handleDisableClick = useCallback(() => {
    onChangeStatus(false);
  }, [onChangeStatus]);

  const disabled = selectedRowKeys.length === 0;

  const items: MenuProps['items'] = useMemo(() => {
    return [
      {
        key: '0',
        onClick: handleEnableClick,
        label: (
          <Flex gap={10}>
            <EnableIcon></EnableIcon>
            <b>{t('enabled')}</b>
          </Flex>
        ),
      },
      {
        key: '1',
        onClick: handleDisableClick,
        label: (
          <Flex gap={10}>
            <DisableIcon></DisableIcon>
            <b>{t('disabled')}</b>
          </Flex>
        ),
      },
      { type: 'divider' },
      {
        key: '2',
        onClick: handleRunClick,
        label: (
          <Flex gap={10}>
            <RunIcon></RunIcon>
            <b>{t('run')}</b>
          </Flex>
        ),
      },
      {
        key: '3',
        onClick: handleCancelClick,
        label: (
          <Flex gap={10}>
            <CancelIcon />
            <b>{t('cancel')}</b>
          </Flex>
        ),
      },
      { type: 'divider' },
      {
        key: '4',
        onClick: handleDelete,
        label: (
          <Flex gap={10}>
            <span className={styles.deleteIconWrapper}>
              <DeleteIcon width={18} />
            </span>
            <b>{t('delete', { keyPrefix: 'common' })}</b>
          </Flex>
        ),
      },
    ];
  }, [
    handleDelete,
    handleRunClick,
    handleCancelClick,
    t,
    handleDisableClick,
    handleEnableClick,
  ]);

  const sortIcon =
    sortOrder === 'asc' ? (
      <SortAscendingOutlined />
    ) : sortOrder === 'desc' ? (
      <SortDescendingOutlined />
    ) : (
      <SwapOutlined />
    );

  return (
    <div className={styles.filter}>
      <Space>
        <Dropdown
          menu={{ items }}
          placement="bottom"
          arrow={false}
          disabled={disabled}
        >
          <Button>
            <Space>
              <b> {t('bulk')}</b>
              <DownOutlined />
            </Space>
          </Button>
        </Dropdown>
        <Button onClick={toggleSortOrder} title="切换排序">
          {sortIcon}
          <span style={{ marginLeft: 6 }}>
            {sortOrder === 'asc'
              ? '升序'
              : sortOrder === 'desc'
                ? '降序'
                : '默认排序'}
          </span>
        </Button>
      </Space>
      <Space>
        <Input
          placeholder={t('searchFiles')}
          value={searchString}
          style={{ width: 220 }}
          allowClear
          onChange={handleInputChange}
          prefix={<SearchOutlined />}
        />

        <Dropdown menu={{ items: actionItems }} trigger={['click']}>
          <Button type="primary" icon={<PlusOutlined />}>
            {t('addFile')}
          </Button>
        </Dropdown>
      </Space>
    </div>
  );
};

export default DocumentToolbar;
