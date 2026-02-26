/**
 * FinVerse AI — 3D Avatar Component
 * Embodied AI avatar using React Three Fiber.
 * Responds to agent states with animations.
 */

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sphere, Ring, Stars } from '@react-three/drei';
import * as THREE from 'three';
import useAppStore from '../../store/appStore';

// Color palette per avatar state
const STATE_COLORS = {
    idle: { primary: '#6c5ce7', secondary: '#a29bfe', emissive: '#3d2fa0' },
    thinking: { primary: '#a855f7', secondary: '#c084fc', emissive: '#7c3aed' },
    searching: { primary: '#00d2ff', secondary: '#3a7bd5', emissive: '#0077b6' },
    analyzing: { primary: '#ffab40', secondary: '#ff8f00', emissive: '#e65100' },
    alert: { primary: '#ff5252', secondary: '#ff1744', emissive: '#b71c1c' },
    recommending: { primary: '#00e676', secondary: '#00c853', emissive: '#1b5e20' },
};

function CoreOrb({ avatarState }) {
    const meshRef = useRef();
    const colors = STATE_COLORS[avatarState] || STATE_COLORS.idle;

    useFrame(({ clock }) => {
        if (!meshRef.current) return;
        const t = clock.getElapsedTime();

        // Different animations per state
        switch (avatarState) {
            case 'thinking':
                meshRef.current.rotation.y = t * 0.5;
                meshRef.current.rotation.x = Math.sin(t * 0.3) * 0.2;
                break;
            case 'searching':
                meshRef.current.rotation.y = Math.sin(t * 2) * 0.5;
                meshRef.current.position.x = Math.sin(t * 1.5) * 0.3;
                break;
            case 'analyzing':
                meshRef.current.rotation.y = t * 0.8;
                meshRef.current.scale.setScalar(1 + Math.sin(t * 3) * 0.05);
                break;
            case 'alert':
                meshRef.current.scale.setScalar(1 + Math.sin(t * 8) * 0.08);
                meshRef.current.position.x = Math.sin(t * 10) * 0.05;
                break;
            case 'recommending':
                meshRef.current.rotation.y = t * 0.3;
                meshRef.current.position.y = Math.sin(t) * 0.1;
                break;
            default: // idle
                meshRef.current.rotation.y = t * 0.2;
                meshRef.current.position.x = 0;
                meshRef.current.position.y = Math.sin(t * 0.5) * 0.05;
                meshRef.current.scale.setScalar(1);
                break;
        }
    });

    const distortSpeed = useMemo(() => {
        switch (avatarState) {
            case 'thinking': return 3;
            case 'searching': return 5;
            case 'analyzing': return 4;
            case 'alert': return 8;
            case 'recommending': return 2;
            default: return 1.5;
        }
    }, [avatarState]);

    const distortAmount = useMemo(() => {
        switch (avatarState) {
            case 'thinking': return 0.4;
            case 'searching': return 0.5;
            case 'analyzing': return 0.3;
            case 'alert': return 0.6;
            case 'recommending': return 0.2;
            default: return 0.25;
        }
    }, [avatarState]);

    return (
        <Sphere ref={meshRef} args={[1, 64, 64]}>
            <MeshDistortMaterial
                color={colors.primary}
                emissive={colors.emissive}
                emissiveIntensity={0.4}
                roughness={0.1}
                metalness={0.8}
                distort={distortAmount}
                speed={distortSpeed}
                transparent
                opacity={0.9}
            />
        </Sphere>
    );
}

function OrbitalRings({ avatarState }) {
    const groupRef = useRef();
    const colors = STATE_COLORS[avatarState] || STATE_COLORS.idle;

    useFrame(({ clock }) => {
        if (!groupRef.current) return;
        const t = clock.getElapsedTime();

        const speed = avatarState === 'searching' ? 2 : avatarState === 'alert' ? 3 : 1;
        groupRef.current.rotation.z = t * 0.5 * speed;
        groupRef.current.rotation.x = Math.sin(t * 0.3) * 0.3;
    });

    return (
        <group ref={groupRef}>
            <Ring args={[1.3, 1.35, 64]} rotation={[Math.PI / 3, 0, 0]}>
                <meshBasicMaterial color={colors.secondary} transparent opacity={0.3} side={THREE.DoubleSide} />
            </Ring>
            <Ring args={[1.5, 1.54, 64]} rotation={[Math.PI / 2.5, Math.PI / 4, 0]}>
                <meshBasicMaterial color={colors.primary} transparent opacity={0.2} side={THREE.DoubleSide} />
            </Ring>
        </group>
    );
}

function Particles({ avatarState }) {
    const pointsRef = useRef();
    const count = 100;

    const positions = useMemo(() => {
        const arr = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const r = 1.5 + Math.random() * 1.5;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            arr[i * 3 + 2] = r * Math.cos(phi);
        }
        return arr;
    }, []);

    useFrame(({ clock }) => {
        if (!pointsRef.current) return;
        const t = clock.getElapsedTime();
        pointsRef.current.rotation.y = t * 0.1;
        pointsRef.current.rotation.x = Math.sin(t * 0.2) * 0.1;
    });

    const colors = STATE_COLORS[avatarState] || STATE_COLORS.idle;

    return (
        <points ref={pointsRef}>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
            </bufferGeometry>
            <pointsMaterial
                size={0.03}
                color={colors.secondary}
                transparent
                opacity={0.6}
                sizeAttenuation
            />
        </points>
    );
}

export default function FinVerseAvatar() {
    const avatarState = useAppStore((state) => state.avatarState);

    return (
        <div className="avatar-container">
            <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
                <ambientLight intensity={0.3} />
                <pointLight position={[5, 5, 5]} intensity={0.8} />
                <pointLight position={[-5, -5, 5]} intensity={0.3} color="#a29bfe" />

                <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
                    <CoreOrb avatarState={avatarState} />
                </Float>

                <OrbitalRings avatarState={avatarState} />
                <Particles avatarState={avatarState} />
                <Stars radius={10} depth={20} count={200} factor={2} saturation={0} fade speed={1} />
            </Canvas>

            <div className={`avatar-status ${avatarState}`}>
                {avatarState === 'idle' && '● Ready'}
                {avatarState === 'thinking' && '◉ Thinking...'}
                {avatarState === 'searching' && '◎ Searching...'}
                {avatarState === 'analyzing' && '◉ Analyzing...'}
                {avatarState === 'alert' && '⚠ Alert'}
                {avatarState === 'recommending' && '★ Recommending'}
            </div>
        </div>
    );
}
