import React from 'react';

interface AuthorizedImageProps {
  src: string;
  token: string;
  className?: string;
  alt?: string;
}

const AuthorizedImage: React.FC<AuthorizedImageProps> = ({
  src,
  token,
  className,
  alt,
}) => {
  const [imgUrl, setImgUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!src) {
      setImgUrl(null);
      return;
    }
    let isMounted = true;
    fetch(src, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch image');
        return res.blob();
      })
      .then((blob) => {
        if (!isMounted) return;
        const url = URL.createObjectURL(blob);
        setImgUrl(url);
      })
      .catch(() => setImgUrl(null));
    return () => {
      isMounted = false;
      if (imgUrl) URL.revokeObjectURL(imgUrl);
    };
  }, [src, token]);

  console.log('AuthorizedImage src:', imgUrl);

  if (!imgUrl) return null;
  return <img className={className} src={imgUrl} alt={alt || ''} />;
};

export default AuthorizedImage;
