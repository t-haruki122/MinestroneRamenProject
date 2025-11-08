import { useEffect, useRef, useState } from 'react'
import { fetchMusic } from '../api/api'

function Music() {
    const [mood, setMood] = useState("")
    const [musicUrl, setMusicUrl] = useState(null)
    const audioRef = useRef(null);
    const getMusic = async () => {
        try {
            const res = await fetchMusic()
            setMusicUrl(res)
        } catch (error) {
            console.error(error);
        }
    }
    useEffect(() => {
        if (musicUrl && audioRef.current) {
            audioRef.current.load(); // URLが変更されたらオーディオを再ロード
        }
    }, [musicUrl])
     const playMusic = () => {
        if (audioRef.current) {
            audioRef.current.play().catch(error => {
                console.error("Error playing music:", error);
            });
        }
    };
    return (
        <>
            Mood : <input type="text" value={mood} onChange={(e) => setMood(e.target.value)} />
            <button onClick={() => getMusic()}>Load Music</button> 
            <button onClick={playMusic} disabled={!musicUrl}>Play Music</button> 

            {musicUrl && (
                <audio ref={audioRef} controls>
                    <source src={musicUrl} type="audio/mpeg" />
                </audio>
            )}
        </>
    )
}

export default Music
