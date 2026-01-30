
import { useState, useEffect } from 'react';
import { avatarCache } from '../utils/avatarCache';

const useCachedImage = (src, type = 'avatar') => {
    const [imageUrl, setImageUrl] = useState(null);

    useEffect(() => {
        let isMounted = true;

        const load = async () => {
            if (!src) {
                if (isMounted) setImageUrl(null);
                return;
            }

            try {
                const url = await avatarCache.loadImage(src, type);
                if (isMounted) {
                    setImageUrl(url);
                }
            } catch (error) {
                console.error('Error loading cached image:', error);
                if (isMounted) {
                    setImageUrl(null);
                }
            }
        };

        load();

        return () => {
            isMounted = false;
        };
    }, [src, type]);

    return imageUrl;
};

export default useCachedImage;
