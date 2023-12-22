<template>
	<view >
		<view  class="picture">
			<image src="../../pic.jpg" mode="aspectFit"></image>
			<text style="font-size:20px">\nWelcome to Face Recognition & AI Face Swap Mini Program</text>
			<text>\n</text>
			<button  @click="goto">Click to Try</button>
		</view>
		
	</view>
	
</template>

<script>
	export default {
		
		methods: {
			goto() {
				uni.switchTab({ 
				url:'/pages/faceChange/faceChange',
				success:(res)=> { 
				let page = getCurrentPages().pop();  //跳转页面成功之后
				if (!page) return;   
				page.loadData(); //如果页面存在，则重新刷新页面
				}
				});
			}
		},
	}
	
</script>

<style>
	.picture{
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;	
	}
</style>