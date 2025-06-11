import { Skeleton } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';
import {
  AreaHighlight,
  Highlight,
  IHighlight,
  PdfHighlighter,
  PdfLoader,
  Popup,
} from 'react-pdf-highlighter';
import { useGetDocumentUrl } from './hooks';

import { useCatchDocumentError } from '@/components/pdf-previewer/hooks';
import FileError from '@/pages/document-viewer/file-error';
import request from '@/utils/request';
import styles from './index.less';
interface IProps {
  highlights: IHighlight[];
  setWidthAndHeight: (width: number, height: number) => void;
}

const HighlightPopup = ({
  comment,
}: {
  comment: { text: string; emoji: string };
}) =>
  comment.text ? (
    <div className="Highlight__popup">
      {comment.emoji} {comment.text}
    </div>
  ) : null;

const Preview = ({ highlights: state, setWidthAndHeight }: IProps) => {
  const [blobUrl, setBlobUrl] = useState<string>('');
  const url = useGetDocumentUrl();
  const ref = useRef<(highlight: IHighlight) => void>(() => {});
  const error = useCatchDocumentError(url);

  const resetHash = () => {};

  useEffect(() => {
    const fetchPdf = async () => {
      try {
        console.error('PDF fetch error:');
        const res = await request(url, { responseType: 'blob' });
        console.log('PDF fetch <<<<>>>', res);
        const blob = res.data;
        const objectUrl = URL.createObjectURL(blob);
        setBlobUrl(objectUrl);
      } catch (err) {
        console.error('PDF fetch error:', err);
      }
    };

    fetchPdf();

    return () => {
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [url]);

  useEffect(() => {
    if (state.length > 0) {
      ref?.current(state[0]);
    }
  }, [state]);

  return (
    <div className={styles.documentContainer}>
      {blobUrl && (
        <PdfLoader
          url={blobUrl}
          beforeLoad={<Skeleton active />}
          workerSrc="/pdfjs-dist/pdf.worker.min.js"
          errorMessage={<FileError>{error}</FileError>}
        >
          {(pdfDocument) => {
            pdfDocument.getPage(1).then((page) => {
              const viewport = page.getViewport({ scale: 1 });
              setWidthAndHeight(viewport.width, viewport.height);
            });

            return (
              <PdfHighlighter
                pdfDocument={pdfDocument}
                enableAreaSelection={(event) => event.altKey}
                onScrollChange={resetHash}
                scrollRef={(scrollTo) => {
                  ref.current = scrollTo;
                }}
                onSelectionFinished={() => null}
                highlightTransform={(
                  highlight,
                  index,
                  setTip,
                  hideTip,
                  viewportToScaled,
                  screenshot,
                  isScrolledTo,
                ) => {
                  const isTextHighlight = !Boolean(
                    highlight.content && highlight.content.image,
                  );

                  const component = isTextHighlight ? (
                    <Highlight
                      isScrolledTo={isScrolledTo}
                      position={highlight.position}
                      comment={highlight.comment}
                    />
                  ) : (
                    <AreaHighlight
                      isScrolledTo={isScrolledTo}
                      highlight={highlight}
                      onChange={() => {}}
                    />
                  );

                  return (
                    <Popup
                      popupContent={<HighlightPopup {...highlight} />}
                      onMouseOver={(popupContent) =>
                        setTip(highlight, () => popupContent)
                      }
                      onMouseOut={hideTip}
                      key={index}
                    >
                      {component}
                    </Popup>
                  );
                }}
                highlights={state}
              />
            );
          }}
        </PdfLoader>
      )}
    </div>
  );
};

export default memo(Preview);
