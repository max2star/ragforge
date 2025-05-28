import { useFetchNextChunkList, useSwitchChunk } from '@/hooks/chunk-hooks';
import type { PaginationProps } from 'antd';
import { Divider, Flex, Pagination, Space, Spin, message } from 'antd';
import classNames from 'classnames';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import ChunkCard from './components/chunk-card';
import CreatingModal from './components/chunk-creating-modal';
import ChunkToolBar from './components/chunk-toolbar';
import DocumentPreview from './components/document-preview/preview';
import {
  useChangeChunkTextMode,
  useDeleteChunkByIds,
  useGetChunkHighlights,
  useHandleChunkCardClick,
  useUpdateChunk,
} from './hooks';

import styles from './index.less';

const Chunk = () => {
  const [selectedChunkIds, setSelectedChunkIds] = useState<string[]>([]);
  const { removeChunk } = useDeleteChunkByIds();
  const {
    data: { documentInfo, data = [], total },
    pagination,
    loading,
    searchString,
    handleInputChange,
    available,
    handleSetAvailable,
  } = useFetchNextChunkList();
  const { handleChunkCardClick, selectedChunkId } = useHandleChunkCardClick();
  const isPdf = documentInfo?.type === 'pdf';

  const { t } = useTranslation();
  const { changeChunkTextMode, textMode } = useChangeChunkTextMode();
  const { switchChunk } = useSwitchChunk();
  const {
    chunkUpdatingLoading,
    onChunkUpdatingOk,
    showChunkUpdatingModal,
    hideChunkUpdatingModal,
    chunkId,
    chunkUpdatingVisible,
    documentId,
  } = useUpdateChunk();
  const [isMinimized, setIsMinimized] = useState(false);

  const toggleMinimize = () => {
    setIsMinimized((prev) => !prev);
  };

  const onPaginationChange: PaginationProps['onShowSizeChange'] = (
    page,
    size,
  ) => {
    setSelectedChunkIds([]);
    pagination.onChange?.(page, size);
  };

  const selectAllChunk = useCallback(
    (checked: boolean) => {
      setSelectedChunkIds(checked ? data.map((x) => x.chunk_id) : []);
    },
    [data],
  );

  const handleSingleCheckboxClick = useCallback(
    (chunkId: string, checked: boolean) => {
      setSelectedChunkIds((previousIds) => {
        const idx = previousIds.findIndex((x) => x === chunkId);
        const nextIds = [...previousIds];
        if (checked && idx === -1) {
          nextIds.push(chunkId);
        } else if (!checked && idx !== -1) {
          nextIds.splice(idx, 1);
        }
        return nextIds;
      });
    },
    [],
  );

  const showSelectedChunkWarning = useCallback(() => {
    message.warning(t('message.pleaseSelectChunk'));
  }, [t]);

  const handleRemoveChunk = useCallback(async () => {
    if (selectedChunkIds.length > 0) {
      const resCode: number = await removeChunk(selectedChunkIds, documentId);
      if (resCode === 0) {
        setSelectedChunkIds([]);
      }
    } else {
      showSelectedChunkWarning();
    }
  }, [selectedChunkIds, documentId, removeChunk, showSelectedChunkWarning]);

  const handleSwitchChunk = useCallback(
    async (available?: number, chunkIds?: string[]) => {
      let ids = chunkIds;
      if (!chunkIds) {
        ids = selectedChunkIds;
        if (selectedChunkIds.length === 0) {
          showSelectedChunkWarning();
          return;
        }
      }

      const resCode: number = await switchChunk({
        chunk_ids: ids,
        available_int: available,
        doc_id: documentId,
      });
    },
    [switchChunk, documentId, selectedChunkIds, showSelectedChunkWarning],
  );

  const { highlights, setWidthAndHeight } =
    useGetChunkHighlights(selectedChunkId);

  const safeJsonParse = (str: string): Record<string, any> => {
    try {
      const fixedStr = str
        .replace(/([{,])\s*'([^']+?)'\s*:/g, '$1"$2":')
        .replace(/:\s*'([^']*?)'/g, ': "$1"');
      return JSON.parse(fixedStr);
    } catch (e) {
      console.warn('Invalid metadata JSON', e);
      return {};
    }
  };

  const renderValue = (value: any): React.ReactNode => {
    if (Array.isArray(value)) {
      return (
        <table
          style={{
            borderCollapse: 'collapse',
            width: '100%',
            marginTop: 4,
            background: '#fdfdfd',
          }}
        >
          <tbody>
            {value.map((item, index) => (
              <tr key={index}>
                <td
                  style={{
                    border: '1px solid #ccc',
                    padding: 4,
                    verticalAlign: 'top',
                  }}
                >
                  {renderValue(item)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    } else if (typeof value === 'object' && value !== null) {
      return (
        <table
          style={{
            borderCollapse: 'collapse',
            width: '100%',
            marginTop: 4,
            background: '#fdfdfd',
          }}
        >
          <thead>
            <tr>
              <th
                style={{
                  border: '1px solid #ccc',
                  padding: 4,
                  background: '#f3f3f3',
                  textAlign: 'left',
                }}
              >
                Key
              </th>
              <th
                style={{
                  border: '1px solid #ccc',
                  padding: 4,
                  background: '#f3f3f3',
                  textAlign: 'left',
                }}
              >
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(value).map(([k, v]) => (
              <tr key={k}>
                <td
                  style={{
                    border: '1px solid #ccc',
                    padding: 4,
                    verticalAlign: 'top',
                  }}
                >
                  {k}
                </td>
                <td
                  style={{
                    border: '1px solid #ccc',
                    padding: 4,
                    verticalAlign: 'top',
                  }}
                >
                  {renderValue(v)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    } else {
      return <span>{String(value)}</span>;
    }
  };

  const chunkMetaList = useMemo(() => {
    // const selectedChunks = data.filter((chunk) =>
    //   selectedChunkId.includes(chunk.chunk_id),
    // );

    console.log('data >>>', data);

    const firstData = data?.[0] ?? {};
    const mateData = firstData.metadata;
    let parsedMeta: Record<string, any> = {};
    // selectedChunks.forEach((chunk) => {
    const meta = safeJsonParse(mateData || '{}');
    parsedMeta = { ...parsedMeta, ...meta };
    // });

    return Object.entries(parsedMeta).map(([key, value]) => ({
      key,
      value,
    }));
  }, [data, selectedChunkId]);

  return (
    <>
      <div className={styles.chunkPage}>
        <ChunkToolBar
          selectAllChunk={selectAllChunk}
          createChunk={showChunkUpdatingModal}
          removeChunk={handleRemoveChunk}
          checked={selectedChunkIds.length === data.length}
          switchChunk={handleSwitchChunk}
          changeChunkTextMode={changeChunkTextMode}
          searchString={searchString}
          handleInputChange={handleInputChange}
          available={available}
          handleSetAvailable={handleSetAvailable}
        />
        <Divider />
        <Flex flex={1} gap={'middle'}>
          <Flex
            vertical
            className={isPdf ? styles.pagePdfWrapper : styles.pageWrapper}
          >
            <Spin spinning={loading} className={styles.spin} size="large">
              <div className={styles.pageContent}>
                <Space
                  direction="vertical"
                  size={'middle'}
                  className={classNames(styles.chunkContainer, {
                    [styles.chunkOtherContainer]: !isPdf,
                  })}
                >
                  {data.map((item) => (
                    <ChunkCard
                      item={item}
                      key={item.chunk_id}
                      editChunk={showChunkUpdatingModal}
                      checked={selectedChunkIds.some(
                        (x) => x === item.chunk_id,
                      )}
                      handleCheckboxClick={handleSingleCheckboxClick}
                      switchChunk={handleSwitchChunk}
                      clickChunkCard={handleChunkCardClick}
                      selected={item.chunk_id === selectedChunkId}
                      textMode={textMode}
                    />
                  ))}
                </Space>
              </div>
            </Spin>
            <div className={styles.pageFooter}>
              <Pagination
                {...pagination}
                total={total}
                size={'small'}
                onChange={onPaginationChange}
              />
            </div>
          </Flex>
          {/* <Flex
            className={isPdf ? styles.pagePdfWrapper : styles.pageWrapper}
            style={{
              width: isMinimized ? 100 : 600,
              background: '#fafafa',
              borderRadius: 8,
              padding: 16,
              border: '1px solid #eee',
              height: 'fit-content',
              alignSelf: 'flex-start',
              overflowX: 'auto',
              position: 'relative',
            }}
          >
            <Space
              direction="vertical"
              size={'middle'}
              className={classNames(styles.chunkContainer, {
                [styles.chunkOtherContainer]: !isPdf,
              })}
            >
              <div
                onClick={toggleMinimize}
                style={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                {isMinimized ? 'Expand' : 'Min'}
              </div>
              <table
                style={{
                  width: '100%',
                  fontSize: 14,
                  borderCollapse: 'collapse',
                  border: '1px solid #ccc',
                }}
              >
                <thead>
                  <tr>
                    <th
                      style={{
                        textAlign: 'left',
                        padding: 8,
                        background: '#f3f3f3',
                        border: '1px solid #ccc',
                      }}
                    >
                      Key
                    </th>
                    <th
                      style={{
                        textAlign: 'left',
                        padding: 8,
                        background: '#f3f3f3',
                        border: '1px solid #ccc',
                      }}
                    >
                      Value
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {chunkMetaList.map((item) => (
                    <tr key={item.key}>
                      <td
                        style={{
                          padding: 8,
                          border: '1px solid #ccc',
                          verticalAlign: 'top',
                          color: '#555',
                        }}
                      >
                        {item.key}
                      </td>
                      <td
                        style={{
                          padding: 8,
                          border: '1px solid #ccc',
                          verticalAlign: 'top',
                        }}
                      >
                        {renderValue(item.value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Space>
          </Flex> */}
          {isPdf && (
            <section className={styles.documentPreview}>
              <DocumentPreview
                highlights={highlights}
                setWidthAndHeight={setWidthAndHeight}
              />
            </section>
          )}
        </Flex>
      </div>
      {chunkUpdatingVisible && (
        <CreatingModal
          doc_id={documentId}
          chunkId={chunkId}
          hideModal={hideChunkUpdatingModal}
          visible={chunkUpdatingVisible}
          loading={chunkUpdatingLoading}
          onOk={onChunkUpdatingOk}
          parserId={documentInfo.parser_id}
        />
      )}
    </>
  );
};

export default Chunk;
